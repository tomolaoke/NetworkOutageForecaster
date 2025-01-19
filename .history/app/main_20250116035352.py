from fastapi import FastAPI, HTTPException
from datetime import datetime
from .services.weather_service import WeatherService
import uvicorn

app = FastAPI(title="Network Outage Forecaster")
weather_service = WeatherService()

@app.get("/")
async def root():
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "message": "Network Outage Forecaster API"
    }

@app.get("/weather/{lat}/{lon}")
async def get_weather(lat: float, lon: float):
    weather_data = await weather_service.get_current_weather(lat, lon)
    if weather_data is None:
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")
    return weather_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)