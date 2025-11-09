import threading
from collections import deque

from src.aircraft_db import AircraftDatabase
from src.tray import FlightTrackerTray
from src.monitoring_loop import monitoring_loop
from src.opensky import get_token
from src.location import get_my_location

# Shared state between monitoring thread and tray
shared_state = {
    'paused': False,
    'radius_km': 5,
    'tokens_used': 0,
    'recent_flights': deque(maxlen=5),  # Stores only last 5 flights
    'current_aircraft': set()
}

print("=== Flight Tracker Starting ===")
token = get_token()
aircraft_db = AircraftDatabase('data/aircraft-database-complete-2025-08.csv')

# Get user location
print("Getting your location...")
user_lat, user_lon = get_my_location()

if user_lat is None or user_lon is None:
    user_lat, user_lon = 47.61, -122.33
    print(f"Could not get location, using Seattle ({user_lat}, {user_lon})")

print(f"Central location: {user_lat:.4f}, {user_lon:.4f}")
print(f"Starting with {shared_state['radius_km']}km radius")
print("System tray icon will appear shortly...\n")

tray = FlightTrackerTray(shared_state)

# Start monitoring in background thread
monitor_thread = threading.Thread(
    target=monitoring_loop,
    args=(shared_state, aircraft_db, user_lat, user_lon, token, tray),
    daemon=True  # Thread dies when main program exits
)
monitor_thread.start()

# Blocks until exit clicked
tray.run()