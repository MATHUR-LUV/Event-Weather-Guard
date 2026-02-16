from typing import List, Dict
from app.schemas import ForecastHour


# WMO Weather interpretation codes (WW)
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}

def get_condition_description(code: int) -> str:
    return WMO_CODES.get(code, "Unknown Weather")


def calculate_severity(hour: ForecastHour) -> int:
    score = 0

    # 1. Base Score from WMO Codes (Condition Tier)
    if hour.condition_code >= 95: # Thunderstorms
        score = 80
    elif hour.condition_code in [65, 82]: # Heavy/Violent Rain
        score = 70
    elif hour.condition_code in [61, 63, 80, 81]: # Moderate Rain
        score = 40
    elif hour.condition_code >= 1: # Cloudy/Light Drizzle
        score = 15
    else: # Clear
        score = 0

    # 2. Add Wind Penalty (Max +20 points)
    # 50km/h is our dangerous threshold. 
    # We add 4 points for every 10km/h of wind.
    wind_penalty = (hour.wind_kmh / 50) * 20
    score += wind_penalty

    # 3. Add Rain Probability Penalty (Max +10 points)
    # This adds weight to how "certain" the bad weather is.
    prob_penalty = (hour.rain_prob / 100) * 10
    score += prob_penalty

    # 4. Final Cap
    # We ensure the score doesn't exceed 100.
    return int(min(score, 100))


def evaluate_risk(forecasts: List[ForecastHour]) -> Dict:
    reasons = set()
    level = "Safe"
    max_severity = 0
    
    for hour in forecasts:
        sev = calculate_severity(hour)
        if sev > max_severity:
            max_severity = sev

        # --- ❌ UNSAFE CHECK ---
        # Triggered by high severity (100) or specific dangerous WMO codes
        if sev >= 80:
            level = "Unsafe"
            if hour.condition_code >= 95:
                reasons.add(f"Thunderstorm ({hour.condition_desc}) at {hour.time}")
            elif hour.condition_code in [65, 82]:
                reasons.add(f"Extreme/Heavy rain ({hour.condition_desc}) at {hour.time}")
            elif hour.wind_kmh > 50:
                reasons.add(f"Dangerous winds ({hour.wind_kmh} km/h) at {hour.time}")
        
        # --- ⚠️ RISKY CHECK (Only if the overall event isn't already Unsafe) ---
        elif level != "Unsafe" and sev >= 35:
            level = "Risky"
            if hour.rain_prob > 60:
                reasons.add(f"High rain probability ({hour.rain_prob}%) at {hour.time}")
            elif hour.wind_kmh >= 30:
                reasons.add(f"Strong winds ({hour.wind_kmh} km/h) at {hour.time}")
            elif (51 <= hour.condition_code <= 63) or (80 <= hour.condition_code <= 81):
                reasons.add(f"Rain expected ({hour.condition_desc}) at {hour.time}")

    summaries = {
        "Unsafe": "Event should be cancelled or moved indoors due to severe conditions.",
        "Risky": "Outdoor activities are risky. Consider a backup plan.",
        "Safe": "Weather conditions are optimal for an outdoor event."
    }

    return {
        "classification": level,
        "severity_score": max_severity,
        "summary": summaries[level],
        "reason": list(reasons)
    }