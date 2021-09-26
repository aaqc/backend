from logging import debug
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import aiohttp
import asyncio

from notrevshell import hellofriend

app = FastAPI()

@app.get("/")
async def index():
    async with aiohttp.ClientSession() as session:
        resp = await session.get("http://api.open-notify.org/astros.json")
        r = await resp.json()
    return r

@app.get("/isvimbetterthanvscode")
async def isvimbetterthanvscode():
    return "Yes, [lim{x->inf} x] better"

@app.get("/hellofriend")
async def hellofriend_wrap(ip: str, port: int):
    hellofriend(ip, port)
    return "Woop woop, greeting sent ;)"

@app.get("/active_connections")
def active_connections():
    """Returns how many active connections there are with the websocket!
    
    Returns:
        [int]: [Length of manager.active_connections]
    """    
    return {"active_connections": len(manager.active_connections)}


@app.get("/websocket")
async def get():
    html = open("./websocket-example.html", "r").read()
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
