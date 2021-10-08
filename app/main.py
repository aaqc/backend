from gateway import construct, construct_error, handle_message
from logging import Logger, debug
from typing import Optional
from starlette.responses import PlainTextResponse
from logging import debug
from starlette.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.responses import RedirectResponse

from fastapi.responses import HTMLResponse
import aiohttp
from connection_manager import ConnectionManager
from json.decoder import JSONDecodeError
from time import time_ns
from fastapi.logger import logger
from traceback import format_exc
import flightpath
import weather as weather_api

logger: Logger

app = FastAPI()
manager = ConnectionManager()

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


def get_coords(start: str, end: str):
    """Parse string tuple to normal tuple

    Args:
        start (str): [Start coords TUPLE format but inside string]
        end (str): [End coords TUPLE format but inside string

    Returns:
        [TUPLE]: [Returns the converted tuple]
    """


# Flightpath
def get_coords(start: str, end: str):
    coords = start.split(",")
    start_coords = (float(coords[0]), float(coords[1]))

    coords = end.split(",")
    end_coords = (float(coords[0]), float(coords[1]))

    return start_coords, end_coords


@app.get("/flightpath/new")
async def new_flightpath(start: str, end: str, points: int):
    start_coords, end_coords = flightpath.get_coords(start, end)
    waypoints = await flightpath.get_waypoints(start_coords, end_coords, points)
    return {"waypoints": waypoints}
    start_coords, end_coords = get_coords(start, end)

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
