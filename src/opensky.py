import os
import requests
from dotenv import load_dotenv

def get_token():
    """Get OpenSky access token"""
    # load env variables from .env file
    load_dotenv()

    CLIENT_ID = os.getenv('OPENSKY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('OPENSKY_CLIENT_SECRET')

    print('getting access token...')

    token_response = requests.post(
        # token_response.json() will return a dictionary like:
        # {
        #     'access_token': ""
        #     'expires_in': 1800,
        #     'refresh_expires_in': 0,
        #     'token_type': "Bearer",
        #     'not-before-policy': (some value),
        #     'scope': 'profile email'
        # }

        "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token",
        data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        },
        timeout=30
    )

    token = token_response.json()["access_token"]

    print(f"Got token: {token[:10]}... (obviously there is more)")
    
    return token

def get_aircraft_in_area(token: str, bbox: dict[str, float]) -> dict[str, list]:
    """Get aircraft within a bounding box"""
    print("Making authenticated request to OpenSky API...")
    
    response = requests.get(
        "https://opensky-network.org/api/states/all",
        params=bbox,  # Pass the bbox dictionary as params
        headers={"Authorization": f"Bearer {token}"},
        timeout=30
    )

    data = response.json()
    
    return data
