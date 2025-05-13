import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, city):
        """Get current weather for a city"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # For Celsius
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
            
    def get_forecast(self, city):
        """Get 5-day weather forecast for a city"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forecast data: {e}")
            return None
            
    def get_weather_by_coords(self, lat, lon):
        """Get weather for specific coordinates"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

# Example usage
if __name__ == "__main__":
    weather_api = WeatherAPI()
    
    # Test with a city
    weather = weather_api.get_current_weather("London")
    if weather:
        print(f"Current temperature in London: {weather['main']['temp']}°C")
        
    # Test with coordinates
    weather = weather_api.get_weather_by_coords(51.5074, -0.1278)  # London coordinates
    if weather:
        print(f"Current weather in London: {weather['weather'][0]['description']}") 