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

def evaluate_risk(forecasts: List[ForecastHour]) -> Dict:
    reasons = set()
    level = "Safe"
    
    for hour in forecasts:
        # Rule: Unsafe (Thunderstorms or Severe Wind)
        if hour.condition_code >= 95:
            reasons.add(f"Thunderstorm ({hour.condition_desc}) at {hour.time}")
            level = "Unsafe"
            
        # 2. Heavy/Violent Rain (WMO 65, 82)
        elif hour.condition_code in [65, 82]:
            reasons.add(f"Extreme/Heavy rain ({hour.condition_desc}) at {hour.time}")
            level = "Unsafe"
            
        # 3. Dangerous Wind
        elif hour.wind_kmh > 50:
            reasons.add(f"Dangerous winds ({hour.wind_kmh} km/h) at {hour.time}")
            level = "Unsafe"

        # --- ⚠️ RISKY RULES (If not already Unsafe) ---
        if level != "Unsafe":
            # 1. High Probability
            if hour.rain_prob > 60:
                reasons.add(f"High rain probability ({hour.rain_prob}%) at {hour.time}")
                level = "Risky"
            # 2. Moderate Wind
            elif 30 <= hour.wind_kmh <= 50:
                reasons.add(f"Strong winds ({hour.wind_kmh} km/h) at {hour.time}")
                level = "Risky"
            # 3. Moderate Rain/Drizzle (WMO 51-63, 80-81)
            elif (51 <= hour.condition_code <= 63) or (80 <= hour.condition_code <= 81):
                reasons.add(f"Rain expected ({hour.condition_desc}) at {hour.time}")
                level = "Risky"

    summaries = {
        "Unsafe": "Event should be cancelled or moved indoors due to severe conditions.",
        "Risky": "Outdoor activities are risky. Consider a backup plan.",
        "Safe": "Weather conditions are optimal for an outdoor event."
    }

    return {
        "classification": level,
        "summary": summaries[level],
        "reason": list(reasons)
    }