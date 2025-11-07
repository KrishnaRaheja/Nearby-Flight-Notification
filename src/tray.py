import pystray
from PIL import Image, ImageDraw
import webbrowser

from src.helper_funcs import make_radius_handler, make_flight_handler

class FlightTrackerTray:
    """System tray interface for flight tracker"""
    
    def __init__(self, state):
        """
        Initialize tray with shared state
        
        Args:
            state: Dictionary with shared data
        """
        self.state = state
        self.icon = None
    
    def create_icon(self):
        """Create a simple airplane icon"""
        # Create a 64x64 blue square for now
        image = Image.new('RGB', (64, 64), color='#1e90ff')
        return image
    
    def toggle_pause(self, icon, item):
        """Toggle pause/resume searching for nearby planes"""
        self.state['paused'] = not self.state['paused']
        status_str = "paused" if self.state['paused'] else "resumed"
        print(f"\nMonitoring {status_str}")
        icon.menu = self.create_menu()  # Rebuild menu to update text

    def change_radius(self, icon, item, radius):
        """Change monitoring radius"""
        self.state['radius_km'] = radius
        print(f'\nRadius changed to {radius}km')
        icon.menu = self.create_menu()  # Rebuild menu to update text

    def quit_app(self, icon, item):
        """Exit the application"""
        print("\nExiting flight tracker...")
        icon.stop()
    
    def open_flight_link(self, callsign):
        """Open FlightRadar24 link from tray"""
        webbrowser.open(f'https://www.flightradar24.com/{callsign}')
    
    def create_menu(self):
        """Create the system tray menu"""
        # Radius submenu
        radius_items = []
        for r in [1, 2, 5, 8, 10, 15, 20, 30, 40]:  # Options for radius
            # Add checkmark to radius selected
            label = f"{'✓ ' if self.state['radius_km'] == r else '  '}{r} km"
            radius_items.append(
                pystray.MenuItem(label, make_radius_handler(self, r))
            )
        
        # Recent flights submenu
        recent_items = []
        if self.state['recent_flights']:
            for flight in self.state['recent_flights']:
                recent_items.append(
                    pystray.MenuItem(
                        flight['display'],
                        make_flight_handler(self, flight['callsign'])
                    )
                )
        else:
            recent_items.append(pystray.MenuItem('No recent flights', lambda icon, item: None, enabled=False))
        
        # Pause or resume program
        pause_text = "Resume" if self.state['paused'] else "Pause"
        
        # Build main menu
        menu = pystray.Menu(
            pystray.MenuItem('Recent Flights', pystray.Menu(*recent_items)),  # Each flight passed as separate item
            pystray.MenuItem('Set Radius', pystray.Menu(*radius_items)),  # Each radius option passed as separate item
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(pause_text, self.toggle_pause),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', self.quit_app)
        )
        
        return menu
    
    def update_menu(self):
        """Update menu with new state (changes menu whenever flight is 
        added, not just when tray.run() is called.)"""
        if self.icon:
            self.icon.menu= self.create_menu()

    def run(self):
        """Start the system tray icon"""
        self.icon = pystray.Icon(
            'flight_tracker',
            self.create_icon(),
            'Flight Tracker',
            self.create_menu()
        )
        
        # This blocks until icon.stop() is called
        self.icon.run()
