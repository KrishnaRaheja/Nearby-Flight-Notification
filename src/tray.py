import pystray
from PIL import Image, ImageDraw

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
    
    def quit_app(self, icon, item):
        """Exit the application"""
        print("\nExiting flight tracker...")
        icon.stop()
    
    def create_menu(self):
        """Create a simple menu with just Exit"""
        menu = pystray.Menu(
            pystray.MenuItem('Exit', self.quit_app)
        )
        return menu
    
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