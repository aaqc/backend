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

logger: Logger

app = FastAPI()
manager = ConnectionManager()

# Misc
@app.get("/")
async def index():

    return RedirectResponse(url="/docs")


@app.get("/ping")
async def hello():
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


# Flightpath 
@app.get("/flightpath/new")
async def new_flightpath(start: str, end: str, points: int):
    coords = start.split(",")
    start_coords = (float(coords[0]), float(coords[1]))

    coords = end.split(",")
    end_coords = (float(coords[0]), float(coords[1]))

    waypoints = flightpath.get_waypoints(start_coords, end_coords, points) 
    return {"waypoints": waypoints} 


@app.get("/flightpath/distance")
def flightpath_distance(start_coords: tuple[float, float], end_coords: tuple[float, float]):
    dist = flightpath.get_path_distance(start_coords, end_coords)
    return {"distance": dist}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)


