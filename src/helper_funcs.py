def degrees_to_direction(degrees):
    """Convert degrees (0-360) to compass direction (N, NE, E, etc.)"""
    if degrees is None:
        return None

    # 0, 1, 2, 3, 4, 5, 6, 7
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = round(degrees / 45) % 8 # gives index so we can map to directions list
    return directions[index]

def make_radius_handler(tray_obj, radius):
    """Create handler for radius menu item"""
    def handler(icon, item):
        tray_obj.change_radius(icon, item, radius)
    return handler

def make_flight_handler(tray_obj, callsign):
    """Create handler for flight menu item"""
    def handler(icon, item):
        tray_obj.open_flight_link(callsign)
    return handler