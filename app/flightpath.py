#!/usr/bin/python

from starlette.routing import request_response
from config_handler import get_token
import math

import aiohttp
import asyncio
from typing import Awaitable
from typing import Any

google_maps_token = get_token("google_maps")
weather_api_token = get_token("weather_api")


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

def get_delta_angle(dx: float, dy: float) -> float:
    tan = dy / dx 
    angle = math.degrees( math.atan(tan) )

    return angle if angle < 180 else angle - 360 # handle periodicity

def get_new_angle(start_point: tuple, end_point: tuple, cur_angle: float) -> float:
    dx, dy = end_point[0] - start_point[0], end_point[1] - start_point[1]
    d_angle = get_delta_angle(dx, dy)

    return d_angle, d_angle + cur_angle # TODO: do stuff

async def get_waypoints(start_coords: tuple, end_coords: tuple, points: int) -> Awaitable[Any]:
    lat1, lng1 = start_coords
    lat2, lng2 = end_coords

    params = (
        ("path", f"{lat1},{lng1}|{lat2},{lng2}"),
        ("samples", f"{points}"),
        ("key", google_maps_token),
    )

    async with aiohttp.ClientSession() as session:
        async with session.get("https://maps.googleapis.com/maps/api/elevation/json", params=params) as response:
            try:
                points = await response.json()
                return points
            except Exception as err:
                print(err)
                return "Unable to get waypoints." 



def dev_testing():
    if __name__ != "__main__":
        print("No. Just no. Go away.")
        return


    start_coords = (57.690341, 11.974507)
    end_coords = (57.693616, 11.973180)

    # start_coords = (57.704373, 11.984967)
    # end_coords = (57.707228, 11.992337)

    (y, x) = start_coords
    (yh, xh) = end_coords
    dx, dy = xh - x, yh - y

    # TODO: Convert x, y coords mapped to meters in 2D plane

    # print(get_path_distance(start_coords, end_coords))
    # points = get_waypoints(start_coords, end_coords, 10)
    # print(points)
    # print(get_elevation(57.708870,11.974560).text)

    loop = asyncio.get_event_loop()

    dist = get_path_distance(start_coords, end_coords)
    dang = get_delta_angle(dx, dy)
    new_ang = get_new_angle(dang, 90) # if drone is heading north

    print(f"dist: {dist}")
    print(f"d_ang: {dang} deg")
    print(f"new_ang: {new_ang} deg")

async def get_weather(coords: tuple) -> Awaitable[Any]:
    lat, lng = coords
    try:
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&appid={weather_api_token}"
        async with aiohttp.ClientSession() as client:
            r = await client.get(url)
            return await r.json()
    except:
        return {"status":"error"}

def get_coords(start: str, end: str):
    coords = start.split(",")
    start_coords = (float(coords[0]), float(coords[1]))

    coords = end.split(",")
    end_coords = (float(coords[0]), float(coords[1]))

    return start_coords, end_coords


if __name__ == "__main__":
    asyncio.run(get_weather())
    pass
