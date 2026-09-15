"""
KisanMandi Agmarknet Real Data Cleaning, Transformation & Model Training CLI
=============================================================================
Usage:
    python process_real_agmarknet.py [path_to_raw_agmarknet.csv]
"""

import os
import sys
import pandas as pd
from pipeline.config import TARGET_MANDIS, CROP_PROFILES, FEATURE_NAMES, CLASS_NAMES
from pipeline.normalizer import COMMODITY_MAPPING, match_mandi
from pipeline.builder import build_dataset_from_agmarknet
from pipeline.trainer import train_and_evaluate_model

def run_diagnostics(raw_path: str):
    print("\n=======================================================")
    print("        DATA DIAGNOSTICS & MISMATCH INSPECTION         ")
    print("=======================================================")
    df = pd.read_csv(raw_path)
    
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
    print(f"Standardized columns: {list(df.columns)}")
    
    raw_commodities = df['Commodity'].dropna().astype(str).str.strip().unique()
    matched_commodities = {c: COMMODITY_MAPPING[c.lower()] for c in raw_commodities if c.lower() in COMMODITY_MAPPING}
    excluded_commodities = [c for c in raw_commodities if c.lower() not in COMMODITY_MAPPING]
    
    print(f"\n[+] Matched Target Crops ({len(matched_commodities)} variations):")
    for raw, target in matched_commodities.items():
        print(f"    - Raw: '{raw}' -> Mapped: '{target}'")
        
    print(f"\n[-] Sample Non-Target Commodities Excluded ({len(excluded_commodities)} commodities):")
    print(f"    {excluded_commodities[:12]}")
    
    matched_markets = {}
    for _, row in df.iterrows():
        m_name = match_mandi(row.get('State', ''), row.get('District', ''), row.get('Market', ''))
        if m_name:
            matched_markets[str(row.get('Market', ''))] = m_name
            
    print(f"\n[+] Matched Raw Markets for Target Mandis ({len(matched_markets)} distinct entries):")
    for raw_m, canonical in matched_markets.items():
        print(f"    - Raw Market: '{raw_m}' -> Mapped to Mandi: '{canonical}'")
        
    print(f"\n[!] Notice on Mismatches Handled:")
    print(f"    1. 'Thiruvananthapuram' (Kerala) contains 'hapur' substring -> Explicitly rejected (not Hapur Mandi).")
    print(f"    2. 'Prayagraj' (UP) contains 'agra' substring -> Explicitly rejected (not Agra APMC Mandi).")
    print(f"    3. 'Sonepat' vs 'Sonipat', 'Gazipur' vs 'Ghazipur' -> Accurately normalized.")
    print("=======================================================\n")

def main():
    raw_path = sys.argv[1] if len(sys.argv) > 1 else "raw_agmarknet.csv"
    if not os.path.exists(raw_path):
        print(f"Error: Raw CSV file '{raw_path}' not found.")
        sys.exit(1)
        
    run_diagnostics(raw_path)
    
    print("Building calibrated training dataset from real Agmarknet records...")
    df = build_dataset_from_agmarknet(raw_path)
    csv_path = "agricultural_mandi_dataset.csv"
    df.to_csv(csv_path, index=False)
    print(f"[+] Dataset saved to: {csv_path} ({len(df)} samples)")
    
    print("\nTraining and evaluating Random Forest recommender...")
    model, metrics = train_and_evaluate_model(df, export_models=True)
    
    print("\n---------------- Holdout Test Set Performance ----------------")
    print(f"Test Accuracy:       {metrics['test_accuracy'] * 100:.2f}%")
    print(f"Macro F1-Score:      {metrics['f1_macro']:.4f}")
    print(f"Weighted F1-Score:   {metrics['f1_weighted']:.4f}")
    print(f"Mean 5-Fold CV Acc:  {metrics['cv_mean_accuracy']:.4f} (+/- {metrics['cv_std_accuracy']:.4f})")
    print("\nFeature Importances:")
    for item in metrics['feature_importances']:
        print(f"  - {item['feature']:<18}: {item['percentage']}%")
    print("=======================================================\n")

if __name__ == "__main__":
    main()
