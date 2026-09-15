"""
Agmarknet Training Dataset Builder & Synthesizer
"""

import numpy as np
import pandas as pd
from .config import TARGET_MANDIS, CROP_PROFILES
from .normalizer import normalize_commodity, match_mandi
from .economics import haversine_distance, calculate_transport_and_cess, calculate_freshness_adjusted_net
from .policy import determine_ground_truth_action

def build_dataset_from_agmarknet(raw_csv_path: str, farmer_lat: float = 28.6139, 
                                 farmer_lng: float = 77.2090, target_samples: int = 3500, 
                                 random_seed: int = 42) -> pd.DataFrame:
    """
    Transforms raw Agmarknet market observations into realistic farmer operational scenarios.
    """
    np.random.seed(random_seed)
    df = pd.read_csv(raw_csv_path)
    
    # Standardize column names
    col_map = {}
    for c in df.columns:
        cl = c.strip().lower()
        if 'state' in cl: col_map[c] = 'State'
        elif 'district' in cl: col_map[c] = 'District'
        elif 'market' in cl: col_map[c] = 'Market'
        elif 'commodity' in cl: col_map[c] = 'Commodity'
        elif 'modal' in cl: col_map[c] = 'Modal_Price'
        elif 'date' in cl: col_map[c] = 'Arrival_Date'
    df.rename(columns=col_map, inplace=True)
    
    df['clean_crop'] = df['Commodity'].apply(normalize_commodity)
    df['Modal_Price'] = pd.to_numeric(df['Modal_Price'], errors='coerce')
    
    valid_crops_df = df.dropna(subset=['clean_crop', 'Modal_Price']).copy()
    valid_crops_df = valid_crops_df[valid_crops_df['Modal_Price'] > 100].copy()
    
    valid_crops_df['clean_mandi'] = valid_crops_df.apply(
        lambda r: match_mandi(r.get('State', ''), r.get('District', ''), r.get('Market', '')), axis=1
    )
    
    # Empirical modal price distribution per crop
    crop_empirical_prices = {}
    for crop in CROP_PROFILES.keys():
        prices = valid_crops_df[valid_crops_df['clean_crop'] == crop]['Modal_Price'].values
        crop_empirical_prices[crop] = prices if len(prices) > 0 else np.array([CROP_PROFILES[crop]['baseline_price']])
        
    direct_records = valid_crops_df.dropna(subset=['clean_mandi']).copy()
    
    data = []
    mandi_names = list(TARGET_MANDIS.keys())
    samples_per_combo = max(1, target_samples // (len(mandi_names) * len(CROP_PROFILES)))
    
    for mandi_name in mandi_names:
        m_meta = TARGET_MANDIS[mandi_name]
        base_dist = haversine_distance(farmer_lat, farmer_lng, m_meta['lat'], m_meta['lng'])
        
        for crop_name, cfg in CROP_PROFILES.items():
            direct_price_sub = direct_records[
                (direct_records['clean_mandi'] == mandi_name) & 
                (direct_records['clean_crop'] == crop_name)
            ]
            available_prices = direct_price_sub['Modal_Price'].values if len(direct_price_sub) > 0 else crop_empirical_prices[crop_name]
            
            for _ in range(samples_per_combo):
                gross_price = round(float(np.random.choice(available_prices)), 2)
                distance_km = round(float(max(5.0, base_dist + np.random.uniform(-10.0, 25.0))), 1)
                
                p_min, p_max = cfg['perishability']
                perishability = int(np.random.randint(p_min, p_max + 1))
                days_in_storage = int(np.random.randint(0, cfg['max_days'] + 1))
                
                transport_cost, mandi_cess = calculate_transport_and_cess(distance_km, gross_price)
                freshness_net = calculate_freshness_adjusted_net(
                    gross_price, transport_cost, mandi_cess, perishability, days_in_storage
                )
                
                action = determine_ground_truth_action(
                    gross_price, cfg['baseline_price'], freshness_net,
                    perishability, days_in_storage, cfg['max_days']
                )
                
                data.append({
                    'mandi': mandi_name,
                    'crop': crop_name,
                    'gross_price': gross_price,
                    'distance_km': distance_km,
                    'perishability': perishability,
                    'days_in_storage': days_in_storage,
                    'net_earning': freshness_net,
                    'action': int(action)
                })
                
    return pd.DataFrame(data)
