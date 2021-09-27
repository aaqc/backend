from connection_manager import ConnectionManager
from typing import Any, Optional, Union
from time import time_ns
import typing

def handle_data(manager: ConnectionManager, t: str) -> tuple[str, Any]:
    if t == "ping":
        return "pong", None
    elif t == "log":
        return "ack", None
    elif t == "time":
        return "time", {"utc_ns": time_ns()}
    elif t == "who":
        return "who", {
            "clients": list(manager.clients.keys()),
            "providers": list(manager.providers.keys()),
            "count": len(manager.connections),
        }

    raise NotImplementedError("Message t is not implemented")
