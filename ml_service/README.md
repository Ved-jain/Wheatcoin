# KisanMandi Explainable ML Microservice

An explainable agricultural decision microservice powered by **FastAPI** and **Scikit-Learn**, trained on authentic **Agmarknet Mandi Daily Price Feeds** (Data.gov.in).

---

## 1. Architecture & Pipeline Overview

```
[Raw Agmarknet Feed (Data.gov.in / DMI)]
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│               pipeline/normalizer.py                   │
│  - Standardizes 5 target crops (Tomatoes, Wheat, etc.) │
│  - Filters 14 regional APMC mandis                     │
│  - False-positive substring guardrails (Kerala / UP)   │
└────────────────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│               pipeline/economics.py                    │
│  - Haversine great-circle transit distance (km)        │
│  - Tiered freight logistics rates (₹6.0 vs ₹4.5/km)   │
│  - Statutory 2% APMC mandi cess deduction              │
│  - Perishable shelf-life decay depreciation            │
└────────────────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│               pipeline/policy.py                       │
│  - Formulates utility actions: HOLD / SELL 50% / 100%  │
└────────────────────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│               pipeline/trainer.py                      │
│  - 5-Fold Stratified Cross-Validation                  │
│  - Random Forest Classifier (100 Trees, Depth 7)       │
│  - Export recommender.pkl & model_metrics.json         │
└────────────────────────────────────────────────────────┘
```

---

## 2. Feature Schema & Target Policy

### Input Features
1. **`net_earning`**: Net cash margin per quintal after freight transport, statutory cess, and perishable freshness decay deductions.
2. **`distance_km`**: Geospatial distance from farmer origin to APMC Mandi using the Haversine formula.
3. **`perishability`**: Index from 1 (durable grain like Wheat/Mustard) to 10 (rapidly perishable like Tomatoes).
4. **`days_in_storage`**: Number of days inventory has been held post-harvest.

### Action Labels
- `0 (HOLD)`: Depressed spot prices with safe remaining shelf-life.
- `1 (SELL 50%)`: Balanced margin with manageable holding risk; partial liquidation hedges downside.
- `2 (SELL 100%)`: Imminent spoilage hazard or exceptional peak arbitrage premium.

---

## 3. Empirical Model Performance (Real Agmarknet Data)

- **Dataset Samples**: 3,500 calibrated operational scenarios
- **Holdout Test Accuracy**: **96.00%**
- **5-Fold Stratified CV Accuracy**: **93.04%** ($\pm 0.74\%$)
- **Macro F1-Score**: **0.9535**
- **Weighted F1-Score**: **0.9602**

### Feature Importance Breakdown (Gini Impurity Reduction)
- **`days_in_storage`**: **53.6%**
- **`net_earning`**: **25.6%**
- **`perishability`**: **17.0%**
- **`distance_km`**: **3.8%**

---

## 4. Running the Pipeline

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run end-to-end cleaning, dataset synthesis, and retraining
python process_real_agmarknet.py raw_agmarknet.csv

# Start FastAPI Inference Server
uvicorn app:app --reload --port 8000
```
