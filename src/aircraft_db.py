import pandas as pd

class AircraftDatabase:
    """Handles lookups in the OpenSky aircraft database"""
    
    def __init__(self, csv_path: str):
        """Load the aircraft database CSV"""
        print("Loading aircraft database...")
        # Read CSV with error handling for malformed lines
        self.db = pd.read_csv(
            csv_path,
            on_bad_lines='skip', # Skip malformed rows
            engine='python',
            encoding='utf-8'
        )
        
        # Remove quotes from column names
        self.db.columns = self.db.columns.str.strip("'")
        
        # Load only needed columns
        self.db = self.db[['icao24', 'registration', 'manufacturerName', 'model', 'operator']]
        
        # Index by icao24 for fast lookups
        self.db.set_index('icao24', inplace=True)
        print(f"Loaded {len(self.db)} aircraft")
    
    def lookup(self, icao24: str) -> dict | None:
        """Look up aircraft by ICAO24 hex code
        
        Args:
            icao24: Aircraft transponder hex code (e.g., 'a1b2c3')
            
        Returns:
            Dictionary with aircraft info, or None if not found
        """
        try:
            row = self.db.loc[icao24.lower()]
            
            # Helper function to clean empty strings and unknown values
            def clean_value(val):
                if pd.isna(val):
                    return None
                
                # Convert to string and strip quotes and whitespace
                val_str = str(val).strip().strip("'\"")
                
                # Check if empty after stripping (including cases like '')
                if val_str == '':
                    return None
                
                # Filter out "unknown" in any form
                val_lower = val_str.lower()
                if 'unknown' in val_lower or 'unknow' in val_lower:
                    return None
                
                # Return cleaned value (not the original val!)
                return val_str
            
            return {
                'registration': clean_value(row['registration']),
                'manufacturer': clean_value(row['manufacturerName']),
                'model': clean_value(row['model']),
                'operator': clean_value(row['operator'])
            }
        except KeyError:
            # if aircraft not in database
            return None