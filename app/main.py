from typing import Union
from jose.constants import ALGORITHMS
from pydantic.networks import EmailStr
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.operators import concat_op
from models import Waypoint
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
from gateway import construct, handle_message
from fastapi.logger import logger
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from connection_manager import ConnectionManager
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import (
    get_db,
    verify_password,
    fetch_user,
    get_current_user,
    oauth2_scheme,
)
from sqlalchemy import func, insert, select, delete
from jose import jwt
from datetime import datetime, timedelta
from errortypes import *

# JWT Secret
SECRET_KEY = CONFIG["jwt_secret"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=30)

logger: Logger
app = FastAPI()

manager = ConnectionManager()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/me", response_model=schema.User)
async def get_index(user: models.User = Depends(get_current_user)):
    return user


@app.post("/auth", response_model=Union[schema.AuthResponse, None])
async def post_auth(
    # data: schema.UserLogin,
    # request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = fetch_user(db, form_data.username)

    if not user:
        raise UserNotFound

    if not verify_password(user, data.password):
        raise AuthFailure

    return {
        "access_token": jwt.encode(
            {
                "iss": "aaqc",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE_DELTA,
                "sub": user.username,
            },
            SECRET_KEY,
            ALGORITHMS.HS256,
        ),
        "token_type": "bearer",
    }


@app.post("/groups/join/{group_id}")
async def join_group(
    group_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.execute(insert(models.UserGroups).values(user=user.id, group=group_id))
    db.commit()
    return {"success": True}


@app.post("/register")
async def create_new_user(data: schema.CreateUser, db: Session = Depends(get_db)):
    new_data = data.__dict__

    new_data["password_hash"] = bytes(pwd_context.hash(new_data["password"]), "utf8")
    del new_data["password"]

    expr = insert(models.User).values(**new_data)

    try:
        db.execute(expr)
        db.commit()
    except (sqlalchemy.exc, sqlalchemy.orm.exc):
        raise UserCreationFailure

    return {"success": True}  # TODO: return something useful


@app.get("/users", response_model=list[schema.BaseUser])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(
        models.User.id, models.User.email, models.User.full_name, models.User.username
    ).all()
    return users


@app.get("/users/{id}", response_model=schema.User)
async def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user_by_id = db.query(models.User).filter(models.User.id == id).first()
    user_by_id = user_by_id.__dict__ if user_by_id != None else schema.User.__dict__
    return user_by_id


@app.get("/groups", response_model=list[schema.BaseGroup])
async def get_groups(db: Session = Depends(get_db)):
    groups = list(map(lambda x: x.__dict__, db.query(models.Group).all()))
    return groups


@app.get("/group/{id}", response_model=schema.Group)
async def get_group_by_id(id: int, db: Session = Depends(get_db)):
    group_by_id = db.query(models.Group).filter(models.Group.id == id).first()
    group_by_id = group_by_id.__dict__ if group_by_id != None else schema.Group.__dict__
    return group_by_id


@app.get("/drones")
async def get_drones(db: Session = Depends(get_db)):
    drones = list(map(lambda x: x.__dict__, db.query(models.Drone).all()))
    return drones


@app.get("/flightpaths/{drone_id}")
async def get_paths(drone_id: int, db: Session = Depends(get_db)):
    drones = (
        db.query(models.FlightPath).filter(models.FlightPath.drone == drone_id).all()
    )
    return drones


@app.get("/waypoints/{flightpath_id}")
async def get_waypoints(flightpath_id: int, db: Session = Depends(get_db)):
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
                await websocket.send_json(
                    APIJSONDecodeError().compose_response()
                )
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
    weather = await weather_api.get_weather_at_coords(lat, lng)
    return weather


@app.exception_handler(API_Error)
async def api_error_handler(request: Request, exc: API_Error):
    return exc.compose_response()


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
