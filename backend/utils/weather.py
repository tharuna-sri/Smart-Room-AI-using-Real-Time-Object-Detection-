import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_weather_data(lat, lon):
    """
    Get weather data from OpenWeatherMap API
    """
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')
    if not api_key:
        return None
        
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            return {
                'temperature': data['main']['temp'],
                'conditions': data['weather'][0]['main'].lower(),
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
        return None
        
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return None 