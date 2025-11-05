import json

# Load airline codes once when module is imported
with open('data/airline_codes.json', 'r') as f:
    AIRLINE_CODES = json.load(f)

def extract_airline_code(callsign):
    """Extract airline code from callsign (e.g., 'SWA3491' -> 'SWA')"""
    if not callsign:
        return None
    
    airline_code = ""
    for char in callsign:
        if char.isalpha():
            airline_code += char
        else:
            break
    
    return airline_code.upper() if airline_code else None

def get_airline_name(code):
    """Look up airline name by code"""
    return AIRLINE_CODES.get(code.upper())