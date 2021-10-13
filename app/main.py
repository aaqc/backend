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
from sqlalchemy import func

SECRET_KEY = CONFIG["jwt_secret"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logger: Logger
app = FastAPI()

manager = ConnectionManager()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/auth/email", response_model=schema.AuthResponse)
async def post_auth(email: EmailStr, password: str):
    pass


@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = (
        db.query(models.User, models.UserGroup.group)
        .join(models.UserGroup, models.UserGroup.user == models.User.id)
        .all()
    )
    return users


@app.get("/usergroup")
async def get_usergroup(db: Session = Depends(get_db)):
    users = db.query(models.UserGroup.user, models.UserGroup.group).all()
    return users


@app.get("/groups", response_model=list[schema.Group])
async def get_groups(db: Session = Depends(get_db)):
    return list(map(lambda x: x.__dict__, db.query(models.Group, models.User).all()))


@app.get("/users/{id}", response_model=schema.User)
async def get_user(id: int, db: Session = Depends(get_db)):
    return db.query(models.User).get(id).__dict__


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
