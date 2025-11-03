# Install: pip install python-dotenv
import os

import requests
from dotenv import load_dotenv

# load env variables from .env file
load_dotenv()

CLIENT_ID = os.getenv('OPENSKY_CLIENT_ID')
CLIENT_SECRET = os.getenv('OPENSKY_CLIENT_SECRET')

print('getting access token...')

token_response = requests.post(
    "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token",
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    },
    timeout=30
)

# token_response.json() will return a dictionary like:
# {
#     'access_token': ""
#     'expires_in': 1800,
#     'refresh_expires_in': 0,
#     'token_type': "Bearer",
#     'not-before-policy': (some value),
#     'scope': 'profile email'
# }

token = token_response.json()["access_token"]

print(f"Got token: {token[:10]}... (obviously there is more)")

print("Making authenticated request to OpenSky API...")

# Bellevue, WA bounding box
# lamin = 47.57   # South boundary
# lamax = 47.65   # North boundary
# lomin = -122.22 # West boundary (Lake Washington)
# lomax = -122.13 # East boundary (towards Sammamish)

# Greater Seattle area
lamin = 47.41
lamax = 47.79
lomin = -122.48
lomax = -122.16

response = requests.get(
    f"https://opensky-network.org/api/states/all?lamin={lamin}&lamax={lamax}&lomin={lomin}&lomax={lomax}",
    headers={"Authorization": f"Bearer {token}"},
    timeout=30
)

# Check if request was successful
print(f"Response status code: {response.status_code}")

data = response.json()

print(f"Response data: {data}") # debug statement to see response

# Check if states exists and is not None
if data.get('states') is None:
    print("\nNo aircraft found in this area right now.")
else:
    print(f"\nFound {len(data['states'])} aircraft in Bellevue area!")

    # Parse and display each aircraft
    print("\n--- Aircraft Details ---")
    for state in data['states']:
        # Extract the fields we care about
        icao24 = state[0] # Aircraft unique ICAO 24-bit address
        callsign = state[1].strip() if state[1] else "No callsign"  # Flight number
        country = state[2]
        longitude = state[5]
        latitude = state[6]
        altitude_m = state[7] # Altitude in meters (can be None)
        on_ground = state[8] # boolean True/False
        velocity_ms = state[9] # Speed in m/s (can be None)

        # meters to feet, m/s to mph
        altitude_ft = altitude_m * 3.28084 if altitude_m else "Unknown"
        speed_mph = velocity_ms * 2.23694 if velocity_ms else "Unknown"

        # Format altitude
        if altitude_ft != "Unknown":
            altitude_str = f"{altitude_ft:.0f} ft"
        else:
            altitude_str = "On ground" if on_ground else "Unknown altitude"

        # Format speed
        speed_str = f"{speed_mph:.0f} mph" if speed_mph != "Unknown" else "Unknown speed"

        # Print readable info
        print(f"\n{callsign} ({icao24})")
        print(f"  Country: {country}")
        print(f"  Position: {latitude:.4f}, {longitude:.4f}")
        print(f"  Altitude: {altitude_str}")
        print(f"  Speed: {speed_str}")
        print(f"  On Ground: {on_ground}")
