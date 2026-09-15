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

def match_mandi(state_str, dist_str, market_str):
    """
    Resolves raw Agmarknet market/district/state strings to one of 14 canonical APMC mandis.
    Includes explicit guardrails against substring collisions:
      - 'Thiruvananthapuram' contains 'hapur', but is in Kerala -> rejected.
      - 'Prayagraj' contains 'agra', but is Allahabad -> rejected.
    """
    s = str(state_str).lower().strip()
    d = str(dist_str).lower().strip()
    m = str(market_str).lower().strip()
    
    # 1. Azadpur Mandi
    if ('delhi' in s or 'delhi' in d) and 'azadpur' in m:
        return 'Azadpur Mandi'
    # 2. Ghazipur Mandi (UP Ghazipur district or Delhi Ghazipur)
    if ('ghazipur' in d or 'gazipur' in m):
        return 'Ghazipur Mandi'
    # 3. Narela Mandi
    if 'narela' in m or 'narela' in d:
        return 'Narela Mandi'
    # 4. Okhla Mandi
    if 'okhla' in m or 'okhla' in d:
        return 'Okhla Mandi'
    # 5. Najafgarh Mandi
    if 'najafgarh' in m or 'najafgarh' in d:
        return 'Najafgarh Mandi'
    # 6. Karnal APMC Mandi
    if d == 'karnal' or m == 'karnal' or 'tarori' in m:
        return 'Karnal APMC Mandi'
    # 7. Panipat Mandi
    if d == 'panipat' or m == 'panipat' or 'samalkha' in m:
        return 'Panipat Mandi'
    # 8. Sonipat Mandi
    if d == 'sonipat' or 'sonepat' in m or 'sonipat' in m or 'ganaur' in m:
        return 'Sonipat Mandi'
    # 9. Rohtak Grain Market
    if d == 'rohtak' or 'rohtak' in m:
        return 'Rohtak Grain Market'
    # 10. Meerut Mandi
    if d == 'meerut' or 'meerut' in m:
        return 'Meerut Mandi'
    # 11. Hapur Mandi (Guardrail: prevent false match with Thiruvananthapuram in Kerala)
    if (d == 'hapur' or m == 'hapur') and 'thiruvananthapuram' not in d:
        return 'Hapur Mandi'
    # 12. Bulandshahr Mandi
    if 'bulandshah' in d or 'bulandshah' in m or m in ['gulavati', 'sikarpur', 'anoop shahar', 'jahangirabad']:
        return 'Bulandshahr Mandi'
    # 13. Agra APMC Mandi (Guardrail: match exact district/market 'agra', reject Prayagraj)
    if d == 'agra' or m == 'agra' or m in ['achnera', 'fatehabad']:
        return 'Agra APMC Mandi'
    # 14. Alwar Krishi Mandi
    if d == 'alwar' or 'alwar' in m or m == 'barodamev':
        return 'Alwar Krishi Mandi'
    return None

