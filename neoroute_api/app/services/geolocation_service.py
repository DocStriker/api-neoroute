from geopy.geocoders import Nominatim

class GeolocationService:

    def __init__(self):
        self.geolocator = Nominatim(user_agent="neoroute")

    def get_coordinates(self, address):
        location = self.geolocator.geocode(address)
        if location:
            return {
                "lat": location.latitude,
                "lng": location.longitude
            }
        return None