import os
import sys
import requests
from dotenv import load_dotenv

def get_token():
    """Get OpenSky access token"""
    # load env variables from .env file
    load_dotenv()

    CLIENT_ID = os.getenv('OPENSKY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('OPENSKY_CLIENT_SECRET')

    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: Missing OpenSky credentials in .env file")
        sys.exit(1)

    print('getting access token...')

    try:
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

        token_response.raise_for_status() # Raises http error if raised
        token_data = token_response.json()

        if "access_token" not in token_data:
            print("ERROR: Token response missing access_token field")
            sys.exit(1)

        token = token_data["access_token"]
        print(f"Got token: {token[:10]}... (obviously more to this token))")
        return token

    # Specifies timeout error
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out while getting token")
        sys.exit(1)

    # Handles no connection, DNS resolution fails, Network unreachable, and more.
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to OpenSky API (try checking your wifi?)")
        sys.exit(1)

    # Different HTTP error handling
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: HTTP error {e.response.status_code}")
        status = e.response.status_code
        if status == 401:
            print("Invalid credentials - check your .env file")
        elif status == 403:
            print("Access forbidden - your account may not have API access")
        elif status == 429:
            print("Rate limit exceeded - too many requests")
            print("Wait a few minutes and try again")
        elif status == 500:
            print("OpenSky server error - try again later")
        elif status == 503:
            print("OpenSky service temporarily unavailable")
        else:
            print(f"Unexpected error code: {status}")
        sys.exit(1)

    # All unhandled exceptoins
    except Exception as e:
        print(f"ERROR: Unexpected error getting token: {e}")
        sys.exit(1)

def get_aircraft_in_area(token: str, bbox: dict[str, float]) -> dict[str, list] | None:
    """Get aircraft within a bounding box"""
    print("Making authenticated request to OpenSky API...")

    try:
        response = requests.get(
            "https://opensky-network.org/api/states/all",
            params=bbox,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )

        response.raise_for_status()
        data = response.json()
        return data

    except requests.exceptions.Timeout:
        print("WARNING: API request timed out, will retry next cycle")
        return None

    except requests.exceptions.ConnectionError:
        print("WARNING: Connection error, will retry next cycle")
        return None

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        print(f"WARNING: HTTP error {status}")

        if status == 401:
            print("Token may have expired - you may need to restart the app")
        elif status == 429:
            print("Rate limit exceeded - reduce polling frequency or wait")
        elif status >= 500:
            print("OpenSky server error - not your fault")

        return None

    except Exception as e:
        print(f"WARNING: Error fetching aircraft data: {e}")
        return None
