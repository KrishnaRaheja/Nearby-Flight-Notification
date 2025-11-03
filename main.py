# Install: pip install python-dotenv
from src.location import get_my_location, calculate_bounding_box
from src.opensky import get_token, get_aircraft_in_area

# Get token
token = get_token()

# Get user location
print("Getting your location...")
my_lat, my_lon = get_my_location()

if my_lat is None or my_lon is None:
    print("Could not get location, using default (Seattle)")
    my_lat, my_lon = 47.61, -122.33

print(f"Central location: {my_lat:.4f}, {my_lon:.4f}")

radius_km = 5  # 5km radius around you

# Calculate bounding box
bounding_box = calculate_bounding_box(my_lat, my_lon, radius_km)
print(f"Searching within a {radius_km}km radius...")

# Get aircraft data
data = get_aircraft_in_area(token, bounding_box)

# Check if states exists and is not None
if data.get('states') is None:
    print("\nNo aircraft found in this area right now.")
else:
    print(f"\nFound {len(data['states'])} aircraft in your area!")

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
