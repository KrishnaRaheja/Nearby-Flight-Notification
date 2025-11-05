from geopy.distance import distance
import time
import json

from src.aircraft_db import AircraftDatabase
from src.location import calculate_bounding_box, get_my_location
from src.opensky import get_aircraft_in_area, get_token
from plyer import notification
from src.airline_lookup import extract_airline_code, get_airline_name
from src.helper_funcs import degrees_to_direction

# Load airline codes
with open('data/airline_codes.json', 'r') as f:
    AIRLINE_CODES = json.load(f)

# Setup
print("=== Flight Tracker Starting ===")
token = get_token()
aircraft_db = AircraftDatabase('data/aircraft-database-complete-2025-08.csv')

# Get user location
print("Getting your location...")
user_lat, user_lon = get_my_location()

if user_lat is None or user_lon is None:
    print("Could not get location, using default (Seattle)")
    user_lat, user_lon = 47.61, -122.33

print(f"Central location: {user_lat:.4f}, {user_lon:.4f}")

radius_km = 50  # Radius around user (can be changed by user)
print(f"Monitoring for aircraft within {radius_km}km...")
print("Press Ctrl+C to stop\n")

# Track which aircraft we've already notified about
seen_aircraft = set()
user_pos = (user_lat, user_lon)

# Main monitoring loop
try:
    while True:
        # Calculate bounding box
        bounding_box = calculate_bounding_box(user_lat, user_lon, radius_km)
        
        # Get aircraft data
        data = get_aircraft_in_area(token, bounding_box)
        
        if data.get('states') is None:
            print("No aircraft in area...")
        else:
            current_aircraft = set()  # Aircraft currently in range
            new_count = 0
            
            for state in data['states']:
                icao24 = state[0]
                plane_lat = state[6]
                plane_lon = state[5]
                
                if plane_lat and plane_lon: # if either is None, skip, cannot find position anyway
                    plane_pos = (plane_lat, plane_lon)
                    dist_to_plane_km = distance(user_pos, plane_pos).km
                    
                    # Only process aircraft within user specified radius
                    if dist_to_plane_km <= radius_km:
                        current_aircraft.add(icao24)
                        
                        # Is this a NEW aircraft?
                        if icao24 not in seen_aircraft:
                            # Extract data for notification
                            callsign = state[1].strip() if state[1] else "No callsign"
                            altitude_m = state[7]
                            on_ground = state[8]
                            velocity_ms = state[9]
                            heading_degrees = state[10]
                            
                            # Convert units
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
                            
                            # Build notification title
                            title_parts = []
                            
                            if aircraft_info:
                                # Either "Boeing 737", "737", or "Boeing" (whatever is availible)
                                if aircraft_info['manufacturer'] and aircraft_info['model']:
                                    model_str = f"{aircraft_info['manufacturer']} {aircraft_info['model']}"
                                    title_parts.append(model_str)
                                elif aircraft_info['model']:
                                    title_parts.append(aircraft_info['model'])
                                elif aircraft_info['manufacturer']:
                                    title_parts.append(aircraft_info['manufacturer'])
                            
                            # Build notification title with operator
                            if operator:
                                if title_parts:
                                    notif_title = f"{title_parts[0]} - {operator}"
                                else:
                                    notif_title = f"{operator}"
                            else:
                                if title_parts:
                                    notif_title = f"{title_parts[0]}"
                                else:
                                    notif_title = f"{callsign}"
                            
                            # Build notification message (shorter for Windows)
                            notif_message = f"{callsign} • {altitude_str or 'Unknown alt'} • {dist_to_plane_km:.1f} km"
                            
                            # Show notification
                            notification.notify(
                                title=notif_title,
                                message=notif_message,
                                timeout=10
                            )
                            
                            # Print to console too
                            print(f"✈️   {notif_title}")
                            print(f"    {notif_message}")
                            print(f"    View: https://www.flightradar24.com/{callsign}\n")
                            
                            # Mark as seen
                            seen_aircraft.add(icao24)
                            new_count += 1
            
            # Status update
            if new_count > 0:
                print(f"[{new_count} new aircraft detected]")
            else:
                print(f"[Monitoring... {len(current_aircraft)} aircraft in range]")
        
        # Wait 15 seconds before next check
        time.sleep(15)

except KeyboardInterrupt:
    print("\n\nStopping flight tracker...")