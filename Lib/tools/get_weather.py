"""
Get current weather for a city
"""
import os
import sys
import json

from Lib.base.base import tool

@tool(
    name="get_weather",
    description="Get current weather for a city",
    schema={
    "type": "object",
    "properties": {
        "city": {
            "type": "string",
            "description": "City name"
        }
    },
    "required": [
        "city"
    ]
}
)
def get_weather(city: str) -> str:
    try:
        import httpx, json
        g = httpx.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1").json()
        if not g.get("results"): return f"City '{city}' not found"
        r = httpx.get(f"https://api.open-meteo.com/v1/forecast?latitude={g['results'][0]['latitude']}&longitude={g['results'][0]['longitude']}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m").json()
        c = r["current"]
        return json.dumps({"city": g["results"][0]["name"], "temp": f"{c['temperature_2m']}C", "humidity": f"{c['relative_humidity_2m']}%", "wind": f"{c['wind_speed_10m']} km/h"}, indent=2)
    except Exception as e: return f"Error: {e}"