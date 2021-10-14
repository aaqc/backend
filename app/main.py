from pydantic.networks import EmailStr
import schema
import models
from config_handler import CONFIG
import weather as weather_api
import uvicorn
import flightpath
from traceback import format_exc
from starlette.responses import RedirectResponse
from starlette.responses import PlainTextResponse
from logging import Logger
from json.decoder import JSONDecodeError
from gateway import construct, construct_error, handle_message
from fastapi.logger import logger
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.security import OAuth2PasswordBearer
from connection_manager import ConnectionManager
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import func, insert

SECRET_KEY = CONFIG["jwt_secret"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logger: Logger
app = FastAPI()

manager = ConnectionManager()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/auth/email", response_model=schema.AuthResponse)
async def post_auth_email(email: EmailStr, password: str):
    pass


@app.post("/auth/username", response_model=schema.AuthResponse)
async def post_auth_username(username: str, password: str):
    pass


@app.post("/register")
async def create_new_user(data: schema.CreateUser, db: Session = Depends(get_db)):

    new_data = data.__dict__

    new_data["password_hash"] = bytes(pwd_context.hash(new_data["password"]), "utf8")
    del new_data["password"]

    expr = insert(models.User).values(**new_data)

    db.execute(expr)
    db.commit()
    return {"success": True}


@app.get("/users", response_model=list[schema.User])
async def get_users(db: Session = Depends(get_db)):
    users: list[schema.User] = []
    for user in db.query(models.User):

        group_ids = map(
            lambda x: x.group,
            db.query(models.UserGroup).filter(models.UserGroup.user == user.id).all(),
        )

        groups: list[schema.BaseGroup] = []

        for group_id in group_ids:
            group = db.query(models.Group).filter(models.Group.id == group_id).one()
            groups.append(schema.BaseGroup(**group.__dict__))

        users.append(
            schema.User(
                **user.__dict__,
                groups=groups,
            )
        )
    return users


@app.get("/usergroup")
async def get_usergroup(db: Session = Depends(get_db)):
    users = db.query(models.UserGroup.user, models.UserGroup.group).all()
    return users


@app.get("/groups", response_model=list[schema.Group])
async def get_groups(db: Session = Depends(get_db)):
    return list(map(lambda x: x.__dict__, db.query(models.Group, models.User).all()))


@app.get("/users/{id}")
async def get_user(id: int, db: Session = Depends(get_db)):
    #     db.query(models.User, models.UserGroup.group)
    # .join(models.UserGroup, models.UserGroup.user == models.User.id)
    # .filter(models.User.id == id)
    # .all()
    user = (
        db.query(
            models.User.id,
            models.User.email,
            models.User.full_name,
            models.UserGroup.group,
        )
        .filter(models.User.id == id)
        .all()
    )
    groups = (
        db.query(models.UserGroup.group).filter(models.UserGroup.user == id).first()
    )
    return user, groups


# Misc
@app.get("/")
async def index():
    return RedirectResponse(url="/docs")


@app.get("/ping")
async def ping():
    return PlainTextResponse("pong")


# Websocket
@app.websocket("/gateway")
async def connect_client_to_gateway(websocket: WebSocket):
    con_id = await manager.connect_client(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
            except JSONDecodeError:
                await websocket.send_json(construct_error("json-decode-error"))
                continue

            try:
                await websocket.send_json(handle_message(data, manager))
            except Exception:
                logger.error(format_exc())
                await websocket.send_json(construct_error("generic-error"))

    except WebSocketDisconnect:
        await manager.disconnect_client(con_id)
        await manager.broadcast(construct("disconnect", {"id": con_id}))


@app.get("/gateway")
async def status_of_gateway():
    return {"online": True}


@app.get("/gateway/connections")
def active_connections():
    """Returns how many clients and providers are connected to this gateway"""
    return {"count": len(manager.connections)}


@app.get("/flightpath/new")
async def new_flightpath(start: str, end: str, points: int):
    start_coords, end_coords = flightpath.get_coords(start, end)
    waypoints = await flightpath.get_waypoints(start_coords, end_coords, points)
    return {"waypoints": waypoints}


@app.get("/flightpath/distance")
def flightpath_distance(start: str, end: str):
    start_coords, end_coords = flightpath.get_coords(start, end)
    dist = flightpath.get_path_distance(start_coords, end_coords)
    return {"distance": dist}


@app.get("/get_weather_at_coords")
async def get_weather(lat: float, lng: float):
    weather = await weather_api.get_weather_at_coords(lat, lng)
    return weather


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
