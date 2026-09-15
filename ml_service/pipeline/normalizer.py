"""
Data Normalization & Cleaning Module for Agmarknet Raw Feeds
"""

# Agmarknet Raw Commodity Name Variations to Project Canonical Names
COMMODITY_MAPPING = {
    'wheat': 'Wheat',
    'mustard': 'Mustard',
    'mustard seed': 'Mustard',
    'potato': 'Potatoes',
    'potatoes': 'Potatoes',
    'onion': 'Onions',
    'onions': 'Onions',
    'tomato': 'Tomatoes',
    'tomatoes': 'Tomatoes'
}

def normalize_commodity(raw_name: str) -> str:
    """Maps raw Agmarknet commodity strings to canonical project names."""
    if not raw_name or not isinstance(raw_name, str):
        return None
    return COMMODITY_MAPPING.get(raw_name.strip().lower(), None)
