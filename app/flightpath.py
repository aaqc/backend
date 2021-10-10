#!/usr/bin/python

from config_handler import SECRETS
import math

import aiohttp

google_maps_token = SECRETS["google_maps"]
weather_api_token = SECRETS["weather_api"]

# Flightpath
def get_coords(start: str, end: str):
    """Parse string tuple to normal tuple

    Args:
        start (str): [Start coords TUPLE format but inside string]
        end (str): [End coords TUPLE format but inside string

    Returns:
        [TUPLE]: [Returns the converted tuple]
    """
    coords = start.split(",")
    start_coords = (float(coords[0]), float(coords[1]))

    coords = end.split(",")
    end_coords = (float(coords[0]), float(coords[1]))

    return start_coords, end_coords


def get_path_distance(start_coords: tuple, end_coords: tuple) -> dict:
    lat1, lng1 = start_coords
    lat2, lng2 = end_coords

    # Earth Radius
    earth_radius = 6371

    lat_diffrance = math.radians(lat2 - lat1)
    lng_diffrance = math.radians(lng2 - lng1)

    lat1_radian = math.radians(lat1)
    lat2_radian = math.radians(lat2)

    haversine_formula = pow(math.sin(lat_diffrance / 2), 2) + pow(
        math.sin(lng_diffrance / 2), 2
    ) * math.cos(lat1_radian) * math.cos(lat2_radian)

    c = 2 * math.asin(math.sqrt(haversine_formula))

    return {"km": earth_radius * c, "m": earth_radius * c * 1000}


def get_delta_angle(dx: float, dy: float) -> float:
    tan = dy / dx
    angle = math.degrees(math.atan(tan))

    return angle if angle < 180 else angle - 360  # handle periodicity


def get_new_angle(
    start_point: tuple, end_point: tuple, cur_angle: float
) -> tuple[float, float]:
    dx, dy = end_point[0] - start_point[0], end_point[1] - start_point[1]
    d_angle = get_delta_angle(dx, dy)

    return d_angle, d_angle + cur_angle  # TODO: do stuff


async def get_waypoints(start_coords: tuple, end_coords: tuple, points: int):
    lat1, lng1 = start_coords
    lat2, lng2 = end_coords

    params = (
        ("path", f"{lat1},{lng1}|{lat2},{lng2}"),
        ("samples", f"{points}"),
        ("key", google_maps_token),
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://maps.googleapis.com/maps/api/elevation/json", params=params
        ) as response:
            try:
                waypoints = await response.json()
                return waypoints
            except Exception as err:
                print(err)
                return {"error": "Unable to get waypoints."}
