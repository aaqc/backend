import traceback
from fastapi.security import oauth2
from aaqc.auth import create_token, decode_token
from aaqc.database import create_group, fetch_user
from aaqc.utils import use_current_user, check_login
import aaqc.schema as schema
import aaqc.models as models
from aaqc.errortypes import GroupNotFound
from config_handler import CONFIG
import aaqc.api.flightpath as flightpath
import uvicorn
from traceback import format_exc, print_exc
from starlette.responses import PlainTextResponse
from logging import Logger
from json.decoder import JSONDecodeError
from aaqc.ws.gateway import construct, handle_message
from fastapi.logger import logger
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from aaqc.ws.connection_manager import ConnectionManager
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from aaqc.utils import use_db
from sqlalchemy import insert
from aaqc.errortypes import *
from sqlalchemy.exc import SQLAlchemyError
from fastapi.middleware.cors import CORSMiddleware

# JWT Secret
SECRET_KEY = CONFIG["jwt_secret"]
ALGORITHM = "HS256"

logger: Logger
app = FastAPI()
oauth2_scheme = oauth2.OAuth2PasswordBearer(tokenUrl="auth")

origins = ["http://localhost", "http://localhost:3000", "https://dash.aaqc.ml", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


manager = ConnectionManager()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/me", response_model=schema.User)
async def get_index(user: models.User = Depends(use_current_user)):
    return user


@app.post("/auth")
async def post_auth(
    form_data: oauth2.OAuth2PasswordRequestForm = Depends(),
    # request: Request,
    db: Session = Depends(use_db),
    # form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = fetch_user(db, form_data.username)

    if not user:
        raise UserNotFound

    if not check_login(db, form_data.username, form_data.password):
        raise AuthFailure

    return {"access_token": create_token(user.email), "token_type": "bearer"}


@app.post("/refresh", response_model=schema.AuthResponse)
async def post_refresh_auth(old_token: str, db: Session = Depends(use_db)):
    ident = decode_token(old_token)
    if ident:
        user = fetch_user(db, ident)
        if user:
            return {
                "access_token": create_token(user.email),
                "token_type": "bearer",
            }


@app.delete("/me", response_model=schema.BaseResponse)
async def delete_user(
    user: models.User = Depends(use_current_user), db: Session = Depends(use_db)
):
    db.query(models.User).filter(models.User.id == user.id).delete()
    db.commit()


@app.post("/groups/join/{group_id}")
async def join_group(
    group_id: int,
    user: models.User = Depends(use_current_user),
    db: Session = Depends(use_db),
):
    try:
        db.execute(insert(models.UserGroups).values(user=user.id, group=group_id))
    except SQLAlchemyError:
        raise GroupJoinFailure
    db.commit()
    return {"success": True}


@app.post("/groups/new")
async def _create_group(
    data: schema.CreateGroup,
    current_user: models.User = Depends(use_current_user),
    db: Session = Depends(use_db),
):
    return create_group(db, data.name, current_user)


@app.post("/register", response_model=schema.AuthResponse)
async def create_new_user(data: schema.CreateUser, db: Session = Depends(use_db)):
    new_data = data.__dict__

    new_data["password_hash"] = bytes(pwd_context.hash(new_data["password"]), "utf8")
    del new_data["password"]

    if db.query(models.User.email).filter_by(email=data.email).first() is not None:
        raise EmailUnavailableError
    expr = insert(models.User).values(**new_data)

    try:
        cursor = db.execute(expr)
        create_group(db, data.name + "'s Group", cursor.inserted_primary_key[0])

    except SQLAlchemyError as error:
        print_exc()
        raise UserCreationFailure
    db.commit()

    return {
        "access_token": create_token(data.email),
    }


@app.get("/users", response_model=list[schema.User])
async def get_users(db: Session = Depends(use_db)):
    users = db.query(models.User).all()
    return users


@app.get("/users/{id}", response_model=schema.User)
async def get_user_by_id(id: int, db: Session = Depends(use_db)):
    user_by_id = db.query(models.User).filter(models.User.id == id).first()
    user_by_id = user_by_id.__dict__ if user_by_id != None else schema.User.__dict__
    return user_by_id


@app.get("/groups", response_model=list[schema.Group])
async def get_groups(db: Session = Depends(use_db)):
    groups = list(map(lambda x: x.__dict__, db.query(models.Group).all()))
    return groups


@app.get("/group/{id}", response_model=schema.Group)
async def get_group_by_id(id: int, db: Session = Depends(use_db)):
    group_by_id = db.query(models.Group).filter(models.Group.id == id).one_or_none()
    if not group_by_id:
        raise GroupNotFound
    return group_by_id


@app.get("/drones")
async def get_drones(db: Session = Depends(use_db)):
    drones = list(map(lambda x: x.__dict__, db.query(models.Drone).all()))
    return drones


@app.get("/flightpaths/{drone_id}")
async def get_paths(drone_id: int, db: Session = Depends(use_db)):
    drones = (
        db.query(models.FlightPath).filter(models.FlightPath.drone == drone_id).all()
    )
    return drones


@app.get("/waypoints/{flightpath_id}")
async def get_waypoints(flightpath_id: int, db: Session = Depends(use_db)):
    waypoint = (
        db.query(models.Waypoint).filter(models.Waypoint.path == flightpath_id).first()
    )
    return waypoint


# Misc
# @app.get("/")
# async def index():
#     return RedirectResponse(url="/docs")


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
                await websocket.send_json(APIJSONDecodeError().compose_response())
                continue

            try:
                await websocket.send_json(handle_message(data, manager))
            except Exception:
                logger.error(format_exc())
                await websocket.send_json(GenericError().compose_response())

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
    weather = await flightpath.get_weather_at_coords(lat, lng)
    return weather


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return exc.compose_response()


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
