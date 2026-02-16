import httpx
from fastapi import HTTPException
from app.schemas import Location

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

async def fetch_weather_data(location: Location):
    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "hourly": "precipitation_probability,wind_speed_10m,weather_code",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPEN_METEO_URL, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()["hourly"]
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Weather service currently unreachable")