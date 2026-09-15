"""
Configuration & Constants for APMC Mandis and Crop Profiles
"""

# Canonical 14 Target Mandis with GPS Coordinates (matching seed.js)
TARGET_MANDIS = {
    "Azadpur Mandi": {"state": "Delhi", "district": "North Delhi", "lat": 28.7136, "lng": 77.1780},
    "Ghazipur Mandi": {"state": "Delhi", "district": "East Delhi", "lat": 28.6256, "lng": 77.3312},
    "Narela Mandi": {"state": "Delhi", "district": "North West Delhi", "lat": 28.8528, "lng": 77.0911},
    "Okhla Mandi": {"state": "Delhi", "district": "South East Delhi", "lat": 28.5494, "lng": 77.2736},
    "Najafgarh Mandi": {"state": "Delhi", "district": "South West Delhi", "lat": 28.6090, "lng": 76.9855},
    "Karnal APMC Mandi": {"state": "Haryana", "district": "Karnal", "lat": 29.6857, "lng": 76.9905},
    "Panipat Mandi": {"state": "Haryana", "district": "Panipat", "lat": 29.3909, "lng": 76.9635},
    "Sonipat Mandi": {"state": "Haryana", "district": "Sonipat", "lat": 28.9931, "lng": 77.0151},
    "Rohtak Grain Market": {"state": "Haryana", "district": "Rohtak", "lat": 28.8955, "lng": 76.6066},
    "Meerut Mandi": {"state": "Uttar Pradesh", "district": "Meerut", "lat": 28.9845, "lng": 77.7064},
    "Hapur Mandi": {"state": "Uttar Pradesh", "district": "Hapur", "lat": 28.7306, "lng": 77.7759},
    "Bulandshahr Mandi": {"state": "Uttar Pradesh", "district": "Bulandshahr", "lat": 28.4070, "lng": 77.8498},
    "Agra APMC Mandi": {"state": "Uttar Pradesh", "district": "Agra", "lat": 27.1767, "lng": 78.0081},
    "Alwar Krishi Mandi": {"state": "Rajasthan", "district": "Alwar", "lat": 27.5530, "lng": 76.6346}
}

# Core Crop Profiles & Economic Baselines (INR / quintal)
CROP_PROFILES = {
    'Wheat': {'baseline_price': 2275, 'perishability': (1, 2), 'max_days': 45},
    'Mustard': {'baseline_price': 5450, 'perishability': (1, 3), 'max_days': 45},
    'Potatoes': {'baseline_price': 1550, 'perishability': (3, 5), 'max_days': 30},
    'Onions': {'baseline_price': 2200, 'perishability': (4, 6), 'max_days': 25},
    'Tomatoes': {'baseline_price': 3100, 'perishability': (8, 10), 'max_days': 10},
}

FEATURE_NAMES = ['net_earning', 'distance_km', 'perishability', 'days_in_storage']
CLASS_NAMES = ['HOLD', 'SELL 50%', 'SELL 100%']
