    # Step 4: Parse and display each aircraft
    print("\n--- Aircraft Details ---")
    for state in data['states']:
        # Extract the fields we care about
        icao24 = state[0]           # Unique ID
        callsign = state[1].strip() if state[1] else "No callsign"  # Flight number
        country = state[2]
        longitude = state[5]
        latitude = state[6]
        altitude_m = state[7]       # Altitude in meters (can be None)
        on_ground = state[8]        # True/False
        velocity_ms = state[9]      # Speed in m/s (can be None)

        # Convert units to human-readable
        altitude_ft = altitude_m * 3.28084 if altitude_m else "Unknown"
        speed_mph = velocity_ms * 2.23694 if velocity_ms else "Unknown"

        # Format altitude nicely
        if altitude_ft != "Unknown":
            altitude_str = f"{altitude_ft:.0f} ft"
        else:
            altitude_str = "On ground" if on_ground else "Unknown altitude"

        # Format speed nicely
        speed_str = f"{speed_mph:.0f} mph" if speed_mph != "Unknown" else "Unknown speed"

        # Print readable info
        print(f"\n{callsign} ({icao24})")
        print(f"  Country: {country}")
        print(f"  Position: {latitude:.4f}, {longitude:.4f}")
        print(f"  Altitude: {altitude_str}")
        print(f"  Speed: {speed_str}")
        print(f"  On Ground: {on_ground}")