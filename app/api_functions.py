from time import time_ns
from connection_manager import ConnectionManager
from typing import Awaitable

import flightpath

# async 
loop = asyncio.get_event_loop()

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

# Flightpath data functions
def get_coords(data):
    start_coords = ( float(data["start"]["lat"]), float(data["start"]["lng"]) )
    end_coords = ( float(data["end"]["lat"]), float(data["end"]["lng"]) )

    return start_coords, end_coords


# Flightpath API wrappers
def get_distance(data):
    start_coords, end_coords = get_coords(data)

    distance_dict = flightpath.get_path_distance(start_coords, end_coords)
    return "distance", distance_dict


def get_waypoints(data):
    start_coords, end_coords = get_coords(data)
    points = int(data["points"])

    waypoints = loop.run_until_complete( flightpath.get_waypoints(start_coords, end_coords, points) )
    return "waypoints", waypoints


functions = {
    "ping": ping,
    "time": time,
    "who": who,
    "get_distance", get_distance,
    "get_waypoints", get_waypoints
}
