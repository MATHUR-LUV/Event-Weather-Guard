import pytest
from app.schemas import ForecastHour
from app.services.logic import evaluate_risk

def test_safe_weather():
    # Base 0 + Wind (15/50 * 20 = 6) + Prob (10/100 * 10 = 1) = 7
    hours = [ForecastHour(
        time="12:00", 
        rain_prob=10, 
        wind_kmh=15, 
        condition_code=0, 
        condition_desc="Clear sky"
    )]
    result = evaluate_risk(hours)
    assert result["classification"] == "Safe"
    assert result["severity_score"] < 35

def test_risky_rain_high_prob():
    # Base 15 (Overcast) + Wind (10/50 * 20 = 4) + Prob (70/100 * 10 = 7) = 26
    # Wait: Overcast isn't Moderate Rain. To get "Risky" (>35), 
    # let's use a condition code for Moderate Rain (61) or higher prob/wind.
    hours = [ForecastHour(
        time="14:00", 
        rain_prob=90, 
        wind_kmh=35, 
        condition_code=61, # Slight rain (Base 40)
        condition_desc="Slight rain"
    )]
    result = evaluate_risk(hours)
    assert result["classification"] == "Risky"
    # Severity should be Base 40 + Wind ~14 + Prob 9 = 63
    assert 40 <= result["severity_score"] < 80

def test_unsafe_thunderstorm_granular():
    # Base 80 + Wind (20/50 * 20 = 8) + Prob (80/100 * 10 = 8) = 96
    hours = [ForecastHour(
        time="16:00",
        rain_prob=80,
        wind_kmh=20,
        condition_code=95,
        condition_desc="Thunderstorm"
    )]
    result = evaluate_risk(hours)
    assert result["classification"] == "Unsafe"
    assert result["severity_score"] >= 80

def test_mixed_conditions_priority():
    hours = [
        ForecastHour(time="17:00", rain_prob=0, wind_kmh=5, condition_code=0, condition_desc="Clear"),
        # This will hit 100 because of max cap
        ForecastHour(time="18:00", rain_prob=95, wind_kmh=65, condition_code=96, condition_desc="Severe Storm")
    ]
    result = evaluate_risk(hours)
    assert result["classification"] == "Unsafe"
    assert result["severity_score"] == 100

def test_severity_components():
    """Verifies that wind and probability actually increase the score."""
    low_wind = [ForecastHour(time="10:00", rain_prob=50, wind_kmh=10, condition_code=95, condition_desc="Storm")]
    high_wind = [ForecastHour(time="10:00", rain_prob=50, wind_kmh=45, condition_code=95, condition_desc="Storm")]
    
    res_low = evaluate_risk(low_wind)
    res_high = evaluate_risk(high_wind)
    
    # High wind should yield a higher score than low wind for the same storm
    assert res_high["severity_score"] > res_low["severity_score"]