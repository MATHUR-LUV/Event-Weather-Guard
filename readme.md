# 🛡️ Event Weather Guard

**Will It Rain During My Event?**

Event Weather Guard is a professional backend service for event organizers. It analyzes hourly weather forecasts and provides deterministic safety classifications for outdoor events like festivals, sports matches, and marathons.

## ✨ Features

- 📊 **Hourly weather analysis**
- 🧠 **Deterministic risk classification**
- ⚡ **Fast and stateless API**
- 🐳 **Docker-ready deployment**
- 📚 **Auto-generated Swagger docs**


## 🚀 Setup \& Installation

### ✅ Option 1: Docker (Recommended)

1. **Clone the repository**

```bash
git clone https://github.com/MATHUR-LUV/Event-Weather-Guard.git
cd Event-Weather-Guard
```

2. **Launch with Docker Compose**

```bash
docker-compose up --build
```

3. **Access the service**
    - **API Endpoint**: POST : http://localhost:8000/event-forecast
    - **Swagger Docs**: http://localhost:8000/docs

### 🧪 Option 2: Local Development (Python)

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Run the server**

```bash
uvicorn app.main:app --reload
```


## 🔌 API Usage

**`POST /event-forecast`**

Analyzes weather conditions for a given event window.

### 📥 Request Body

```json
{
  "name": "Community Football Match",
  "location": {
    "latitude": 19.0760,
    "longitude": 72.8777
  },
  "start_time": "2026-02-18T16:00:00",
  "end_time": "2026-02-18T18:00:00"
}
```


### 📤 Successful Response

```json
{
  "classification": "Risky",
  "summary": "Outdoor activities are risky. Consider a backup plan.",
  "reason": ["High rain probability (85%) at 17:00"],
  "event_window_forecast": [
    {
      "time": "17:00",
      "rain_prob": 85,
      "wind_kmh": 12.5,
      "condition_code": 61,
      "condition_desc": "Slight rain"
    }
  ]
}
```


## 🧠 Weather Classification Rules

The system evaluates every hour within the event window. If any hour triggers a rule, the entire event is escalated to the **highest risk level**:

**Unsafe > Risky > Safe**

### ❌ Unsafe

*Immediate danger to life or property.*

**Triggered when:**

- Thunderstorms (WMO 95–99)
- Heavy/Violent Rain (WMO 65, 82)
- Wind speed **> 50 km/h**


### ⚠️ Risky

*Significant potential for disruption.*

**Triggered when:**

- Rain probability **> 60%**
- Moderate Rain/Drizzle (WMO 51–63, 80–81)
- Wind speed **30–50 km/h**


### ✅ Safe

*Ideal outdoor conditions.*

**Condition:** No Unsafe or Risky thresholds met during the event window.

## ⚖️ Key Assumptions \& Trade-offs

| Aspect | Details |
| :-- | :-- |
| **📅 Forecast Horizon** | Designed for events within the next **7–10 days**. Requests too far in past/future return `400 Bad Request` |
| **🔢 Deterministic Logic** | Uses fixed thresholds for consistency. Easily configurable for event-specific sensitivity (e.g., kite festivals are more wind-sensitive) |
| **🧩 Stateless Design** | No database used. No event persistence. **Highly scalable and lightweight** |
| **🌐 API Dependency** | Uses [Open-Meteo public API](https://open-meteo.com/).

## 🛠️ Tech Stack

- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Validation**: Pydantic v2
- **Weather Source**: Open-Meteo API
- **Containerization**: Docker \& Docker Compose

***