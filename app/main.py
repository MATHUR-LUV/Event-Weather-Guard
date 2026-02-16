from fastapi import FastAPI, HTTPException
from datetime import datetime
from app.schemas import EventRequest, WeatherAdvisory, ForecastHour
from app.services.weather_api import fetch_weather_data
from app.services.logic import evaluate_risk, get_condition_description

app = FastAPI(title="Event Weather Guard")

@app.post("/event-forecast", response_model=WeatherAdvisory)
async def analyze_event_weather(event: EventRequest):
    raw_data = await fetch_weather_data(event.location)

    event_window = []
    for i, time_str in enumerate(raw_data["time"]):
        forecast_time = datetime.fromisoformat(time_str)
        
        if event.start_time <= forecast_time <= event.end_time:
            code = raw_data["weather_code"][i]
            event_window.append(ForecastHour(
                time=forecast_time.strftime("%H:%M"),
                rain_prob=raw_data["precipitation_probability"][i],
                wind_kmh=raw_data["wind_speed_10m"][i],
                condition_code=code,
                condition_desc=get_condition_description(code)
            ))

    if not event_window:
        raise HTTPException(status_code=400, detail="Requested time window is out of forecast range.")

    analysis = evaluate_risk(event_window)
    return {**analysis, "event_window_forecast": event_window}