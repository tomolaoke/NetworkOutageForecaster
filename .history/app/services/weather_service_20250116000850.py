import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Optional

load_dotenv()

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            raise ValueError("OpenWeather API key not found in environment variables")

    async def get_current_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch current weather data for given coordinates
        """
        try:
            response = requests.get(
                f"{self.base_url}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant weather data
            return {
                "timestamp": datetime.now().isoformat(),
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "weather_condition": data["weather"][0]["main"],
                "weather_description": data["weather"][0]["description"],
                "rain_last_hour": data.get("rain", {}).get("1h", 0),
                "clouds": data["clouds"]["all"]
            }
        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            return None