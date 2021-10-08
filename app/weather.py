import aiohttp
import asyncio
from typing import Awaitable
from typing import Any
from config_handler import TOKENS

weather_api_token = TOKENS["weather_api"]


async def get_weather_at_coords(lat: float, lng: float) -> Awaitable[dict[str, Any]]:
    try:
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}&appid={weather_api_token}"
        async with aiohttp.ClientSession() as client:
            r = await client.get(url)
            return await r.json()
    except:
        return {"status": "error"}
