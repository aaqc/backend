from logging import debug
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from typing import Optional
app = FastAPI()

@app.get("/")
def index():
    return {"Test": "Test"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/websocket")
async def get():
    html = open("./app/websocket-example.html", "r").read()
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, debug=True)