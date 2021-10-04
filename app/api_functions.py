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

def get_new_angle(data):
    start_coords, end_coords = get_coords(data)
    cur_angle = float(data["cur_angle"])

    d_angle = flightpath.get_new_angle(start_coords, end_coords, cur_angle)
    return "angle" 

def get_delta_angle(data):
    dx, dy = float(data["dx"]), float(data["dy"])

    d_angle = flightpath.get_delta_angle(dx, dy)
    return "d_angle", d_angle

def get_waypoints(data):
    start_coords, end_coords = get_coords(data)
    num_points = int(data["points"])
    pass

functions = {
    "ping": ping,
    "time": time,
    "who": who,
    "get_distance", get_distance,
    "get_delta_angle", get_delta_angle,
    "get_new_angle", get_new_angle,
}
