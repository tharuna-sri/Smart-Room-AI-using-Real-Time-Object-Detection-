import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from datetime import datetime

class TravelRecommender:
    def __init__(self):
        # Initialize with sample data (in production, this would be loaded from a database)
        self.destinations = self._load_sample_destinations()
        self.user_preferences = {}
        
    def _load_sample_destinations(self):
        # Sample destination data with features
        return pd.DataFrame([
            {
                'id': 1,
                'name': 'Bali, Indonesia',
                'type': 'beach',
                'climate': 'tropical',
                'activities': ['surfing', 'yoga', 'temple_visits'],
                'best_season': 'summer',
                'budget_level': 'medium',
                'popularity': 0.9
            },
            {
                'id': 2,
                'name': 'Paris, France',
                'type': 'city',
                'climate': 'temperate',
                'activities': ['museums', 'shopping', 'dining'],
                'best_season': 'spring',
                'budget_level': 'high',
                'popularity': 0.95
            },
            {
                'id': 3,
                'name': 'Kyoto, Japan',
                'type': 'cultural',
                'climate': 'temperate',
                'activities': ['temples', 'gardens', 'tea_ceremony'],
                'best_season': 'spring',
                'budget_level': 'medium',
                'popularity': 0.85
            }
        ])
    
    def _calculate_season_score(self, destination, current_weather):
        # Calculate how suitable the destination is for the current season
        current_month = datetime.now().month
        season = 'winter' if current_month in [12, 1, 2] else \
                'spring' if current_month in [3, 4, 5] else \
                'summer' if current_month in [6, 7, 8] else 'fall'
        
        return 1.0 if destination['best_season'] == season else 0.5
    
    def _calculate_weather_score(self, destination, weather_data):
        # Calculate weather compatibility score
        if not weather_data:
            return 0.5
            
        temp = weather_data.get('temperature', 20)
        conditions = weather_data.get('conditions', 'clear')
        
        # Simple scoring based on temperature and conditions
        temp_score = 1.0 if 15 <= temp <= 30 else 0.5
        conditions_score = 1.0 if conditions in ['clear', 'partly_cloudy'] else 0.7
        
        return (temp_score + conditions_score) / 2
    
    def get_recommendations(self, user_preferences, weather_data, location):
        # Update user preferences
        self.user_preferences.update(user_preferences)
        
        # Calculate scores for each destination
        scores = []
        for _, destination in self.destinations.iterrows():
            # Calculate various scores
            season_score = self._calculate_season_score(destination, weather_data)
            weather_score = self._calculate_weather_score(destination, weather_data)
            
            # Calculate preference match score
            preference_score = 0.5  # Default score
            if 'preferred_type' in user_preferences:
                preference_score = 1.0 if user_preferences['preferred_type'] == destination['type'] else 0.3
            
            # Calculate final score
            final_score = (
                season_score * 0.3 +
                weather_score * 0.3 +
                preference_score * 0.2 +
                destination['popularity'] * 0.2
            )
            
            scores.append({
                'destination': destination.to_dict(),
                'score': final_score
            })
        
        # Sort by score and return top recommendations
        recommendations = sorted(scores, key=lambda x: x['score'], reverse=True)
        return recommendations[:5]  # Return top 5 recommendations 