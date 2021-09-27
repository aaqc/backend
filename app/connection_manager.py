from typing import Any
from fastapi.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.clients: dict[int, WebSocket] = dict()

        self.providers: dict[int, WebSocket] = dict()
        """A provider is someone with data to transmit to clients (for example our drone)"""
        self.id_counter = 0

    @property
    def connections(self):
        """Return all connections, both clients and providers"""
        return self.clients | self.providers

    async def connect_client(self, websocket: WebSocket):
        con_id = await self._connect(websocket)
        self.clients[con_id] = websocket
        return con_id

    async def connect_provider(self, websocket: WebSocket):
        con_id = await self._connect(websocket)
        self.providers[con_id] = websocket
        return con_id

    async def _connect(self, websocket: WebSocket):
        await websocket.accept()
        self.id_counter += 1
        con_id = self.id_counter
        await websocket.send_json({"type": "auth", "data": {"id": con_id}})
        await self.broadcast({"type": "connect", "data": {"id": con_id}})
        return con_id

    async def disconnect_client(self, con_id: int):
        await self.clients[con_id].close()
        del self.clients[con_id]

    async def disconnect_provider(self, con_id: int):
        await self.providers[con_id].close()
        del self.providers[con_id]

    async def send(self, payload: Any, con_id: int):
        await self.connections[con_id].send_json(payload)

    async def broadcast(self, payload: Any):
        for connection in self.clients.values():
            await connection.send_json(payload)
