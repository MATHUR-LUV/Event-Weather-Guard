from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Location(BaseModel):
    latitude: float
    longitude: float

class EventRequest(BaseModel):
    name: str
    location: Location
    start_time: datetime
    end_time: datetime

class ForecastHour(BaseModel):
    time: str
    rain_prob: int
    wind_kmh: float
    condition_code: int
    condition_desc: str

class WeatherAdvisory(BaseModel):
    classification: str
    summary: str
    reason: List[str]
    event_window_forecast: List[ForecastHour]
    recommendation: Optional[str] = None
    severity_score: int