from time import time_ns
from connection_manager import ConnectionManager
from typing import Awaitable

import flightpath

# General API stuff
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

# Flightpath API wrappers
def get_distance(data):
    start_coords, end_coords = (data["start"]["lon"], data["start"]["lat"]), (data["end"]["lon"], data["end"]["lat"])
    distance_dict = flightpath.get_path_distance(start_coords, end_coords)
    return "distance", distance_dict["m"]

functions = {
    "ping": ping,
    "time": time,
    "who": who
}
