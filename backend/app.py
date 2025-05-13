from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from model.recommender import TravelRecommender
from utils.weather import get_weather_data
from utils.location import get_location_data

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the recommender system
recommender = TravelRecommender()

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        user_preferences = data.get('preferences', {})
        location = data.get('location', {})
        
        # Get weather data for the location
        weather_data = get_weather_data(location.get('lat'), location.get('lon'))
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            user_preferences=user_preferences,
            weather_data=weather_data,
            location=location
        )
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/weather', methods=['GET'])
def get_weather():
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if not lat or not lon:
            return jsonify({
                'status': 'error',
                'message': 'Latitude and longitude are required'
            }), 400
            
        weather_data = get_weather_data(lat, lon)
        return jsonify({
            'status': 'success',
            'weather': weather_data
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 