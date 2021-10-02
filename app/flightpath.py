#!/usr/bin/python

from token_handler import get_token
# import requests
import math

import aiohttp
# import asyncio

google_maps_token = get_token("google_maps")

def get_path_distance(start_coords: tuple, end_coords: tuple) -> dict:
    lat1, lng1 = start_coords
    lat2, lng2 = end_coords

    #Earth Radius
    earth_radius = 6371
  
    lat_diffrance = math.radians(lat2 - lat1)
    lng_diffrance = math.radians(lng2 - lng1)

    lat1_radian = math.radians(lat1)
    lat2_radian = math.radians(lat2)
 
    haversine_formula = (pow(math.sin(lat_diffrance / 2), 2) + pow(math.sin(lng_diffrance / 2), 2) * math.cos(lat1_radian) * math.cos(lat2_radian))

    c = 2 * math.asin(math.sqrt(haversine_formula))

    return {"km": earth_radius * c, "m": earth_radius * c * 1000 }

def get_delta_angle(dy: float, dist: float) -> float:
    sin = dy / dist
    angle = math.degrees( math.asin(sin) )

    if( angle > 180 ):
        angle -= 360

    return angle

async def get_waypoints(start_coords: tuple, end_coords: tuple, points: int):
    lat1, lng1 = start_coords
    lat2, lng2 = end_coords

    params = (
        ("path", f"{lat1},{lng1}|{lat2},{lng2}"),
        ("samples", f"{points}"),
        ("key", f"{google_maps_token}"),
    )

    async with aiohttp.ClientSession() as session:
        async with session.get("https://maps.googleapis.com/maps/api/elevation/json", data=params) as response:
            try:
                points = await response.json()["results"]
                return points
            except Exception as err:
                print(err)
                return None  # TODO: print out errors etc

if __name__ == "__main__":
    start_coords = (57.690341, 11.974507)
    end_coords = (57.693616, 11.973180)

    (x, y) = start_coords
    (xh, yh) = end_coords
    dy = yh - y

    # TODO: Convert x, y coords mapped to meters in 2D plane

    # print(get_path_distance(start_coords, end_coords))
    # points = get_waypoints(start_coords, end_coords, 10)
    # print(points)
    # print(get_elevation(57.708870,11.974560).text)
    dist = get_path_distance(start_coords, end_coords)["m"]
    dang = get_delta_angle(yh, dist)
    print(dang)
    pass
