# Install: pip install python-dotenv
from geopy.distance import distance

from src.location import calculate_bounding_box, get_my_location
from src.opensky import get_aircraft_in_area, get_token

# Get token
token = get_token()

# Get user location
print("Getting your location...")
user_lat, user_lon = get_my_location()

if user_lat is None or user_lon is None:
    print("Could not get location, using default (Seattle)")
    user_lat, user_lon = 47.61, -122.33

print(f"Central location: {user_lat:.4f}, {user_lon:.4f}")

radius_km = 5  # 5km radius around you

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

    # Using geopy, sort the list by distance to user location
    user_pos = (user_lat, user_lon)
    aircraft_with_distance = []

    for state in data['states']:
        plane_lat = state[6]
        plane_lon = state[5]

        if plane_lat and plane_lon: # if either is None, skip, cannot find position anyway
            plane_pos = (plane_lat, plane_lon)
            dist_to_plane_km = distance(user_pos, plane_pos).km
            
            if dist_to_plane_km <= radius_km:  # Only include if dist from plane within radius
                aircraft_with_distance.append((dist_to_plane_km, state)) # (distance, flight)

    # tuples automatically sort by first element (distance)
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
