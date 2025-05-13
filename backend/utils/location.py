from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_location_data(address):
    """
    Get location data (latitude, longitude) from address using Nominatim
    """
    try:
        geolocator = Nominatim(user_agent="travel_recommender")
        location = geolocator.geocode(address)
        
        if location:
            return {
                'lat': location.latitude,
                'lon': location.longitude,
                'address': location.address
            }
        return None
        
    except GeocoderTimedOut:
        print("Geocoding service timed out")
        return None
    except Exception as e:
        print(f"Error getting location data: {str(e)}")
        return None 