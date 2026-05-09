import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY", "YOUR_API_KEY")

def get_weather(city: str) -> dict:
    """Get current weather for a city"""
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return {
        "city":        data["name"],
        "temperature": data["main"]["temp"],
        "weather":     data["weather"][0]["description"],
    }
