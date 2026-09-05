"""
Agri-Logistics & Liquidation Dataset Generator
Generates realistic Indian APMC mandi scenarios for explainable ML modeling.
Models agricultural price spreads, transport economics, and perishability hazards.
"""

import numpy as np
import pandas as pd

def generate_agricultural_dataset(n_samples=3500, random_state=42):
    np.random.seed(random_state)
    
    # 5 Key Indian Crop archetypes with realistic baseline parameters (INR per quintal)
    crops = {
        'Wheat': {'baseline_price': 2275, 'perishability': (1, 2), 'max_days': 45},
        'Mustard': {'baseline_price': 5450, 'perishability': (1, 3), 'max_days': 45},
        'Potatoes': {'baseline_price': 1550, 'perishability': (3, 5), 'max_days': 30},
        'Onions': {'baseline_price': 2200, 'perishability': (4, 6), 'max_days': 25},
        'Tomatoes': {'baseline_price': 3100, 'perishability': (8, 10), 'max_days': 10},
    }
    
    crop_names = list(crops.keys())
    # Equal distribution across crop archetypes
    selected_crops = np.random.choice(crop_names, size=n_samples)
    
    data = []
    for crop in selected_crops:
        cfg = crops[crop]
        
        # 1. Perishability Index (1 - 10)
        p_min, p_max = cfg['perishability']
        perishability = int(np.random.randint(p_min, p_max + 1))
        
        # 2. Days in Storage (shelf life consumed relative to crop's resilience)
        days_in_storage = int(np.random.randint(0, cfg['max_days'] + 1))
        
        # 3. Mandi Transit Distance (5 km to 150 km)
        distance_km = round(float(np.random.uniform(5.0, 150.0)), 1)
        
        # 4. Gross Market Price (INR / quintal)
        price_noise_pct = np.random.normal(loc=0.0, scale=0.12)
        gross_price = round(float(max(cfg['baseline_price'] * 0.65, cfg['baseline_price'] * (1.0 + price_noise_pct))), 2)
        
        # 5. Transport & Logistics Cost Model
        freight_rate = 6.0 if distance_km <= 40 else 4.5
        transport_cost = distance_km * freight_rate
        mandi_cess = gross_price * 0.02
        
        # 6. Freshness Decay Penalty
        decay_rate_per_day = perishability * 0.006
        total_decay_loss = min(0.85, decay_rate_per_day * days_in_storage)
        
        base_net = max(0.0, gross_price - transport_cost - mandi_cess)
        freshness_adjusted_net = round(float(base_net * (1.0 - total_decay_loss)), 2)
        
        # Price Premium vs Baseline (%)
        premium_pct = round(float(((gross_price - cfg['baseline_price']) / cfg['baseline_price']) * 100.0), 1)
        
        # 7. Ground Truth Utility Policy (Target Action)
        # 0 = HOLD, 1 = SELL 50% (Averaging), 2 = SELL 100% (Liquidate)
        # Spoilage ratio: how much of safe shelf-life has elapsed
        shelf_life_used_ratio = days_in_storage / float(cfg['max_days'])
        
        if (perishability >= 8 and days_in_storage >= 3) or shelf_life_used_ratio >= 0.70:
            # Imminent spoilage: Must sell 100% immediately to avoid total loss
            action = 2
        elif premium_pct >= 10.0 and freshness_adjusted_net >= cfg['baseline_price']:
            # Peak market price: Sell 100% to capture windfall margin
            action = 2
        elif shelf_life_used_ratio <= 0.40 and (premium_pct < -2.0 or freshness_adjusted_net < cfg['baseline_price'] * 0.85):
            # Safe storage capacity remaining + depressed price: HOLD for recovery
            action = 0
        elif shelf_life_used_ratio <= 0.30 and perishability <= 4:
            # Very durable grain/crop with fresh storage: HOLD unless price is exceptional
            action = 0
        else:
            # Moderate margin and balanced risk: SELL 50% (Lock in gains, hedge remaining stock)
            action = 1
            
        # 2% realistic field noise
        if np.random.rand() < 0.02:
            action = int(np.random.choice([0, 1, 2]))
            
        data.append({
            'crop': crop,
            'gross_price': gross_price,
            'distance_km': distance_km,
            'perishability': perishability,
            'days_in_storage': days_in_storage,
            'net_earning': freshness_adjusted_net,
            'premium_pct': premium_pct,
            'action': int(action)
        })
        
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_agricultural_dataset(3500)
    print("Dataset generated successfully!")
    print(f"Total samples: {len(df)}")
    print("\nClass distribution:")
    print(df['action'].value_counts(normalize=True).rename(index={0: 'HOLD (0)', 1: 'SELL 50% (1)', 2: 'SELL 100% (2)'}))
    df.to_csv("agricultural_mandi_dataset.csv", index=False)
    print("\nSaved to agricultural_mandi_dataset.csv")
