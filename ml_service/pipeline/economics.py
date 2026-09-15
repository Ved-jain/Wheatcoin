"""
Agri-Logistics & Economic Valuation Engine
"""

import numpy as np

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes Great Circle distance (in kilometers) between two geographic coordinates
    using the Haversine formula.
    """
    R = 6371.0  # Earth's radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (np.sin(dlat / 2.0) ** 2 +
         np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) *
         np.sin(dlon / 2.0) ** 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return float(R * c)

def calculate_transport_and_cess(distance_km: float, gross_price: float, cess_rate: float = 0.02) -> tuple:
    """
    Computes freight logistics cost and APMC statutory mandi cess.
    Tiered freight rate:
      - <= 40 km: INR 6.0 / km
      - > 40 km:  INR 4.5 / km
    Mandi cess:
      - 2.0% of gross commodity price
    """
    freight_rate = 6.0 if distance_km <= 40.0 else 4.5
    transport_cost = distance_km * freight_rate
    mandi_cess = gross_price * cess_rate
    return transport_cost, mandi_cess

