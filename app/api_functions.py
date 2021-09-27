from time import time_ns
from connection_manager import ConnectionManager

def ping(data):
    return "pong", None

def time(data):
    return "time", {"utc_ns": time_ns()}

def who(data):
    return "who", {
        "clients": list(data["manager"].clients.keys()),
        "providers": list(data["manager"].providers.keys()),
        "count": len(data["manager"].connections),
    }


functions = {
    "ping": ping,
    "time": time,
    "who": who
}
