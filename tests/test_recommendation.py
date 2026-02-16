import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from unittest.mock import patch
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_alternate_time_recommendation():
    """
    Test that if the initial time is Unsafe, the API finds
    a 'Safe' window in the next 24 hours.
    """
    # 1. Properly generate 30 hours of mock data starting from Feb 17
    start_base = datetime(2026, 2, 17, 0, 0)
    mock_times = [(start_base + timedelta(hours=i)).isoformat() for i in range(30)]

    mock_weather_data = {
        "time": mock_times,
        "weather_code": [95, 95, 95, 0, 0, 0] + [0]*24, # Storm then Clear
        "precipitation_probability": [90, 90, 90, 0, 0, 0] + [0]*24,
        "wind_speed_10m": [20, 20, 20, 5, 5, 5] + [5]*24
    }

    # 2. Mock the external API call
    with patch("app.main.fetch_weather_data", return_value=mock_weather_data):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            payload = {
                "name": "Mock Event",
                "location": {"latitude": 19.07, "longitude": 72.87},
                "start_time": "2026-02-17T00:00:00",
                "end_time": "2026-02-17T02:00:00"
            }
            response = await ac.post("/event-forecast", json=payload)
            
    # 3. Assertions
    data = response.json()
    assert response.status_code == 200
    assert data["classification"] == "Unsafe"
    assert data["recommendation"] is not None
    # Based on our mock, the first safe window starts 3 hours later (03:00)
    assert "03:00" in data["recommendation"]