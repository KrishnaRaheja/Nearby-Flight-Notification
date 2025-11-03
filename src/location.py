import requests

# WARNING: ASK FOR PERMISSION BEFORE DOING SO WHEN PROPERLY BUILDING
def get_my_location() -> tuple[float | None, float | None]:
    """Get user's location from IP address"""
    try:
        ip_response = requests.get("http://ip-api.com/json/", timeout=10)
        ip_data = ip_response.json()
        return ip_data['lat'], ip_data['lon']  # Different keys!
    except Exception as e:
        print(f"Error getting location: {e}")
        return None, None

def calculate_bounding_box(user_lat: float, user_lon: float, radius_km: float) -> dict[str, float]:
    """Calculate bounding box around a point
    
    Args:
        lat: User latitude
        lon: User longitude
        radius_km: Radius in kilometers
    
    Returns:
        Dictionary with lamin, lamax, lomin, lomax
    """
    # Approximately 111km per degree of latitude/longitude
    delta = radius_km / 111.0
    
    return {
        'lamin': user_lat - delta,
        'lamax': user_lat + delta,
        'lomin': user_lon - delta,
        'lomax': user_lon + delta
    }
