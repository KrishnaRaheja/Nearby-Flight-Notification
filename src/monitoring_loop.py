from src.location import calculate_bounding_box, get_my_location
from src.opensky import get_aircraft_in_area, get_token
from windows_toasts import Toast, InteractableWindowsToaster, ToastDuration
from src.airline_lookup import extract_airline_code, get_airline_name
from src.helper_funcs import degrees_to_direction
from geopy.distance import distance
import time


def monitoring_loop(state, aircraft_db, user_lat, user_lon, token, tray_obj):
    """Background monitoring loop"""
    seen_aircraft = set()
    user_pos = (user_lat, user_lon)

    print("=== Monitoring Started ===\n")

    try:
        while True:
            # Check if paused
            if state['paused']:
                print("[PAUSED - monitoring stopped]")
                time.sleep(15)
                continue

            # Calculate bounding box
            bounding_box = calculate_bounding_box(user_lat, user_lon, state['radius_km'])

            # Get aircraft data
            data = get_aircraft_in_area(token, bounding_box)
            state['tokens_used'] += 1

            # # Will be None if cannot grab data either, have to think of that
            # if data.get('states') is None:
            #     print(f"No aircraft in area... [Tokens: {state['tokens_used']}]")
            if data is None:
                # Error occurred (already printed in get_aircraft_in_area)
                print(f"Error fetching data, will retry... [Tokens: {state['tokens_used']}]")
            elif data.get('states') is None:
                # API succeeded but no aircraft in range
                print(f"No aircraft in area... [Tokens: {state['tokens_used']}]")
            else:
                current_aircraft = set()  # Aircraft currently in range
                new_count = 0

                for state_vec in data['states']:
                    icao24 = state_vec[0]
                    plane_lat = state_vec[6]
                    plane_lon = state_vec[5]

                    if plane_lat and plane_lon:  # if either is None, skip, cannot find position anyway
                        plane_pos = (plane_lat, plane_lon)
                        dist_to_plane_km = distance(user_pos, plane_pos).km

                        # Only process aircraft within user specified radius
                        if dist_to_plane_km <= state['radius_km']:
                            current_aircraft.add(icao24)

                            # Is this a NEW aircraft?
                            if icao24 not in seen_aircraft:
                                # Extract data for notification
                                callsign = state_vec[1].strip() if state_vec[1] else "No callsign"
                                altitude_m = state_vec[7]
                                on_ground = state_vec[8]
                                velocity_ms = state_vec[9]
                                heading_degrees = state_vec[10]

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
                                    # Either "Boeing 737", "737", or "Boeing" (whatever is available)
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

                                # Build notification message
                                notif_message = f"{callsign} • {altitude_str or 'Unknown alt'} • {dist_to_plane_km:.1f} km"

                                # Show notification
                                toaster = InteractableWindowsToaster('Click to view on FlightRadar24')
                                new_toast = Toast()
                                new_toast.text_fields = [notif_title, notif_message]
                                new_toast.launch_action = f'https://www.flightradar24.com/{callsign}'
                                new_toast.duration = ToastDuration.Default
                                toaster.show_toast(new_toast)

                                # Print to console
                                print(f"✈️  NEW: {notif_title}")
                                print(f"    {notif_message}")
                                print(f"    View: https://www.flightradar24.com/{callsign}\n")

                                # Add to recent flights (for tray menu)
                                state['recent_flights'].append({
                                    'display': f"{notif_title} ({callsign})",
                                    'callsign': callsign
                                })
                                tray_obj.update_menu()

                                # Mark as seen
                                seen_aircraft.add(icao24)
                                new_count += 1

                # Update current aircraft count for tray
                state['current_aircraft'] = current_aircraft

                # Status update in console
                if new_count > 0:
                    print(f"[{new_count} new aircraft detected] [Tokens: {state['tokens_used']}]")
                else:
                    print(f"[Monitoring... {len(current_aircraft)} aircraft in range] [Tokens: {state['tokens_used']}]")

            # Wait 15 seconds before next check so we don't stress CPU
            time.sleep(15)

    except KeyboardInterrupt:
        print("\n\nStopping flight tracker...")