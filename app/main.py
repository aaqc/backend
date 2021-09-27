from gateway import construct, construct_error, handle_message
from logging import Logger, debug
from typing import Optional
from starlette.responses import PlainTextResponse
from logging import debug
from starlette.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import aiohttp
from connection_manager import ConnectionManager
from json.decoder import JSONDecodeError
from time import time_ns
from fastapi.logger import logger
from traceback import format_exc

logger: Logger


app = FastAPI()

manager = ConnectionManager()


@app.get("/")
async def index():
    return {"isvimbetterthanvscode":"yes, but nano is better"}


@app.get("/isvimbetterthanvscode")
async def isvimbetterthanvscode():
    return "Vim is lim[x->inf] x times better., but nano is lim[x->inf] x better than VIM and vscode"


@app.websocket("/gateway")
async def connect_to_gateway(websocket: WebSocket):
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
            except Exception as error:
                logger.error(format_exc())
                await websocket.send_json(construct_error("generic-error"))

    except WebSocketDisconnect:
        await manager.disconnect_client(con_id)
        await manager.broadcast(construct("disconnect", {"id": con_id}))


@app.get("/gateway")
async def status_of_gateway():
    return {"online": True}


@app.get("/ping")
async def hello():
    return PlainTextResponse("pong")


@app.get("/gateway/connections")
def active_connections():
    """Returns how many clients and providers are connected to this gateway"""
    return {"count": len(manager.connections)}


# @app.get("/websocket")
# async def get():
#     html = open("./websocket-example.html", "r").read()
#     return HTMLResponse(html)


# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
#     await manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             await manager.send_personal_message(f"You wrote: {data}", websocket)
#             await manager.broadcast(f"Client #{client_id} says: {data}")
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(f"Client #{client_id} left the chat")


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
