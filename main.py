from geopy.distance import distance

from src.aircraft_db import AircraftDatabase
from src.location import calculate_bounding_box, get_my_location
from src.opensky import get_aircraft_in_area, get_token

from plyer import notification

import json

# Load airline codes
with open('data/airline_codes.json', 'r') as f:
    AIRLINE_CODES = json.load(f)

def extract_airline_code(callsign):
    """Extract airline code from callsign (e.g., 'SWA3491' -> 'SWA')"""
    if not callsign:
        return None
    
    airline_code = ""
    for char in callsign:
        if char.isalpha():
            airline_code += char
        else:
            break
    
    return airline_code.upper() if airline_code else None

def get_airline_name(code):
    """Look up airline name by code"""
    return AIRLINE_CODES.get(code.upper())

def degrees_to_direction(degrees):
    """Convert degrees (0-360) to compass direction (N, NE, E, etc.)"""
    if degrees is None:
        return None

    # 0, 1, 2, 3, 4, 5, 6, 7
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = round(degrees / 45) % 8 # gives index so we can map to directions list
    return directions[index]

# Get token
token = get_token()

# Load aircraft database
aircraft_db = AircraftDatabase('data/aircraft-database-complete-2025-08.csv')

# Get user location
print("Getting your location...")
user_lat, user_lon = get_my_location()

if user_lat is None or user_lon is None:
    print("Could not get location, using default (Seattle)")
    user_lat, user_lon = 47.61, -122.33

print(f"Central location: {user_lat:.4f}, {user_lon:.4f}")

radius_km = 50  # Radius around user (should be set aldready, user can change.)

# Calculate bounding box
bounding_box = calculate_bounding_box(user_lat, user_lon, radius_km)
print(f"Searching within a {radius_km}km radius...")

# Get aircraft data
data = get_aircraft_in_area(token, bounding_box)

# Check if states exists and is not None
if data.get('states') is None:
    print("\nNo aircraft found in this area right now.")
else:
    print(f"\nFound {len(data['states'])} aircraft in your area!")

    # Using geopy, find user and plane distance, then sort by distance (closest first)
    user_pos = (user_lat, user_lon)
    aircraft_with_distance = []

    for state in data['states']:
        plane_lat = state[6]
        plane_lon = state[5]

        if plane_lat and plane_lon: # if either is None, skip, cannot find position anyway
            plane_pos = (plane_lat, plane_lon)
            dist_to_plane_km = distance(user_pos, plane_pos).km
            
            # Removed, or else bounding box would catch aircraft that circle radius misses
            # if dist_to_plane_km <= radius_km:  # Only include if dist from plane within radius
            #     aircraft_with_distance.append((dist_to_plane_km, state)) # (distance, flight)
            aircraft_with_distance.append((dist_to_plane_km, state))

    aircraft_with_distance.sort(key=lambda x: x[0]) # given x, sort by x[0] (distance)

    # Parse and display each aircraft
    print("\n--- Aircraft Details ---")
    for dist_to_plane_km, state in aircraft_with_distance:
        icao24 = state[0] # Aircraft unique ICAO 24-bit address
        callsign = state[1].strip() if state[1] else "No callsign"  # Flight number
        country = state[2]
        longitude = state[5]
        latitude = state[6]
        altitude_m = state[7] # Altitude in meters (can be None)
        on_ground = state[8] # boolean True/False
        velocity_ms = state[9] # Speed in m/s (can be None)
        heading_degrees = state[10] # Heading in degrees (0-360)

        # meters to feet, m/s to mph
        altitude_ft = altitude_m * 3.28084 if altitude_m else None
        speed_mph = velocity_ms * 2.23694 if velocity_ms else None

        heading = degrees_to_direction(heading_degrees)

        # Format altitude
        if altitude_ft:
            altitude_str = f"{altitude_ft:.0f} ft"
        elif on_ground:
            altitude_str = "On ground"
        else:
            altitude_str = None

        # Format speed
        speed_str = f"{speed_mph:.0f} mph" if speed_mph else None
        
        # Look up aircraft in database
        aircraft_info = aircraft_db.lookup(icao24)
        
        # Determine operator (first try database, then fallback to callsign lookup)
        operator = None
        if aircraft_info and aircraft_info['operator']:
            operator = aircraft_info['operator']
        else:
            # Fallback: try to get airline from callsign
            airline_code = extract_airline_code(callsign)
            if airline_code:
                operator = get_airline_name(airline_code)
        
        # Build Line 1: Model - Operator (only if we have data)
        line1_parts = []
        
        if aircraft_info:
            # Either "Boeing 737", "737", or "Boeing" (whatever is availible)
            if aircraft_info['manufacturer'] and aircraft_info['model']:
                model_str = f"{aircraft_info['manufacturer']} {aircraft_info['model']}"
                line1_parts.append(model_str)
            elif aircraft_info['model']:
                line1_parts.append(aircraft_info['model'])
            elif aircraft_info['manufacturer']:
                line1_parts.append(aircraft_info['manufacturer'])
        
        # Build line 1 with operator if available
        if operator:
            if line1_parts:
                line1 = f"✈️  {line1_parts[0]} - {operator}"
            else:
                line1 = f"✈️  {operator}"
        else:
            if line1_parts:
                line1 = f"✈️  {line1_parts[0]}"
            else:
                line1 = f"✈️  {callsign}"
        
        # Build Line 2: Flight details (only include non-None values)
        line2_parts = [f"Flight {callsign}"]
        
        # If altitude_str has a value (not None)
        if altitude_str:
            line2_parts.append(altitude_str)
        
        line2_parts.append(f"{dist_to_plane_km:.1f} km") # user distance to plane
                
        # If speed_str has a value (not None)
        if speed_str:
            line2_parts.append(speed_str)

        # If heading has a value (not None)
        if heading:
            line2_parts.append(f"Heading {heading}")
        
        line2 = " • ".join(line2_parts)
        
        # Line 3: FlightRadar24 link
        fr24_link = f"https://www.flightradar24.com/{callsign}"

        # Print readable info
        print(f"\n{line1}")
        print(f"{line2}")
        print(f"View: {fr24_link}")