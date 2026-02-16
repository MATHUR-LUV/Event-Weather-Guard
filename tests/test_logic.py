import pytest
from app.schemas import ForecastHour
from app.services.logic import evaluate_risk

def test_safe_weather():
    hours = [ForecastHour(
        time="12:00", 
        rain_prob=10, 
        wind_kmh=15, 
        condition_code=0, 
        condition_desc="Clear sky" # Added
    )]
    result = evaluate_risk(hours)
    assert result["classification"] == "Safe"

def test_risky_rain():
    hours = [ForecastHour(
        time="14:00", 
        rain_prob=70, 
        wind_kmh=10, 
        condition_code=3, 
        condition_desc="Overcast" # Added
    )]
    result = evaluate_risk(hours)
    assert result["classification"] == "Risky"
    assert any("High rain probability" in r for r in result["reason"])

def test_unsafe_thunderstorm():
    hours = [ForecastHour(
        time="16:00",
        rain_prob=80,
        wind_kmh=20,
        condition_code=95,
        condition_desc="Thunderstorm"
    )]
    result = evaluate_risk(hours)
    assert result["classification"] == "Unsafe"
    assert any("Thunderstorm" in r for r in result["reason"])

def test_mixed_conditions_priority():
    hours = [
        ForecastHour(time="17:00", rain_prob=0, wind_kmh=5, condition_code=0, condition_desc="Clear"),
        ForecastHour(time="18:00", rain_prob=90, wind_kmh=60, condition_code=96, condition_desc="Severe Storm")
    ]
    result = evaluate_risk(hours)
    assert result["classification"] == "Unsafe"