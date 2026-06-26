#geocoder.py
from geopy.geocoders import Nominatim
import time

geolocator = Nominatim(user_agent="city_noise_app")

def geocode_address(address: str):
    """Converte endereço em coordenadas"""
    try:
        query = f"{address}, Belém, Pará, Brasil"
        location = geolocator.geocode(query)
        if location:
            return {
                "lat": location.latitude,
                "lon": location.longitude,
                "address": location.address
            }
        return None
    except Exception:
        return None


def reverse_geocode(lat: float, lon: float):
    """Converte coordenadas em endereço"""
    try:
        location = geolocator.reverse((lat, lon), exactly_one=True)
        time.sleep(1)  # respeitar limite do Nominatim
        if location:
            return location.address
        return None
    except Exception:
        return None