from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta # Added timedelta for alternate time logic
from app.schemas import EventRequest, WeatherAdvisory, ForecastHour
from app.services.weather_api import fetch_weather_data
from app.services.logic import evaluate_risk, get_condition_description

app = FastAPI(title="Event Weather Guard")

# --- Added Helper Function to keep logic clean and reusable ---
def extract_forecast_window(raw_data, start_t: datetime, end_t: datetime):
    window = []
    for i, time_str in enumerate(raw_data["time"]):
        # Handle potential 'Z' in timestamp from some API responses
        forecast_time = datetime.fromisoformat(time_str.replace("Z", ""))
        
        if start_t <= forecast_time <= end_t:
            code = raw_data["weather_code"][i]
            window.append(ForecastHour(
                time=forecast_time.strftime("%H:%M"),
                rain_prob=raw_data["precipitation_probability"][i],
                wind_kmh=raw_data["wind_speed_10m"][i],
                condition_code=code,
                condition_desc=get_condition_description(code)
            ))
    return window

@app.post("/event-forecast", response_model=WeatherAdvisory)
async def analyze_event_weather(event: EventRequest):
    # 1. Get raw data
    raw_data = await fetch_weather_data(event.location)
    
    # 2. Extract hours within the event window using the helper
    event_window = extract_forecast_window(raw_data, event.start_time, event.end_time)

    if not event_window:
        raise HTTPException(status_code=400, detail="Requested time window is out of forecast range.")

    # 3. Classify and Return
    analysis = evaluate_risk(event_window)
    
    # --- START: Bonus Extension B (Alternate Time Recommendation) ---
    recommendation = None
    # Only search if the current event is not 'Safe'
    if analysis["classification"] != "Safe":
        event_duration = event.end_time - event.start_time
        
        # Look ahead up to 24 hours from the original start time
        for hours_ahead in range(1, 25):
            alt_start = event.start_time + timedelta(hours=hours_ahead)
            alt_end = alt_start + event_duration
            
            alt_window = extract_forecast_window(raw_data, alt_start, alt_end)
            
            # If we found a valid window, check if it is Safe
            if alt_window and len(alt_window) > 0:
                alt_analysis = evaluate_risk(alt_window)
                if alt_analysis["classification"] == "Safe":
                    recommendation = f"Suggested safer window: {alt_start.strftime('%Y-%m-%d %H:%M')} to {alt_end.strftime('%H:%M')}"
                    break 
    # --- END: Bonus Extension B ---

    # We return the original analysis combined with the new bonus fields
    return {
        **analysis, 
        "recommendation": recommendation, # Added recommendation field
        "event_window_forecast": event_window
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}