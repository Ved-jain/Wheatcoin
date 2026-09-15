# 🌾 KisanMandi (Wheatcoin)
### Agri-Fintech Decision Engine & Hybrid Compound AI Copilot

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Node.js](https://img.shields.io/badge/Node.js-18+-339933?logo=node.js&logoColor=white)](https://nodejs.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-47A248?logo=mongodb&logoColor=white)](https://mongodb.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![Test Accuracy](https://img.shields.io/badge/Model_Accuracy-96.00%25-brightgreen)](https://github.com/Ved-jain/Wheatcoin)

KisanMandi is an **Agri-Fintech & Explainable AI (XAI)** decision platform designed to empower Indian farmers and agricultural commodity traders. Instead of relying solely on gross APMC mandi rates, the platform computes **true net pocket earnings** by deducting Haversine transit freight and perishable shelf-life decay, driving a **Hybrid Compound AI System (Random Forest + Google Gemini Copilot)** that calculates continuous selling percentages and tactical trader negotiation tips.

---

## 🏗️ System Architecture

```
[Farmer Location & Harvest Inventory]
                 │
                 ▼ REST API
┌───────────────────────────────────────────────────────────────┐
│               Node.js & Express API Gateway                   │
│  - MongoDB: APMC mandis (with GPS coordinates) & crop prices │
│  - Haversine Great-Circle distance formula (km)               │
│  - Tiered freight logistics deduction (₹6/km vs ₹4.5/km)      │
│  - Perishable freshness decay modeling (0.6%/day * index)     │
└───────────────────────────────────────────────────────────────┘
                 │
                 ▼ POST /predict_action
┌───────────────────────────────────────────────────────────────┐
│           Python FastAPI Explainable ML Microservice          │
│                                                               │
│  [1] Random Forest Classifier (100 Trees, Depth 7)            │
│      - Inputs: net_earning, distance_km, perishability, days  │
│      - Outputs: Action (HOLD/SELL), Confidence, Probabilities │
│      - 5-Fold Stratified CV: 93.04% | Holdout Test: 96.00%    │
│                                                               │
│  [2] Google Gemini AI Agri-Financial Copilot                  │
│      - Inputs: Probabilities + Spoilage Friction + Margin     │
│      - Outputs: Continuous % (e.g. 65%), Trader Advice, Risk  │
└───────────────────────────────────────────────────────────────┘
                 │
                 ▼ JSON Payload
┌───────────────────────────────────────────────────────────────┐
│                 React 18 + Vite Dashboard                     │
│  - Live Mandi Arbitrage Sorting by true net cash in pocket    │
│  - Dynamic continuous liquidation badges (e.g. "SELL 65%")   │
│  - Micro allocation visual progress bar                       │
│  - Interactive 7-day crop price trend charts (Recharts)       │
│  - Full Model Card & Gini Feature Importance Inspector        │
└───────────────────────────────────────────────────────────────┘
```

---

## 📊 Machine Learning Evaluation & Real Agmarknet Data

The classification model was trained on authentic daily commodity price feeds from **Agmarknet (Directorate of Marketing & Inspection, Ministry of Agriculture / Data.gov.in)** across 14 APMC Mandis (Azadpur, Ghazipur, Karnal, Panipat, Sonipat, Agra, Hapur, etc.).

| Metric | Empirical Score | Description |
| :--- | :--- | :--- |
| **5-Fold Stratified CV Accuracy** | **93.04%** ($\pm 0.74\%$) | Rigorous cross-validation across folds |
| **Holdout Test Accuracy** | **96.00%** | Unseen 20% stratified test set |
| **Macro F1-Score** | **0.9535** | Harmonic mean across all 3 utility classes |
| **Weighted F1-Score** | **0.9602** | Class-distribution weighted F1 |

### Gini Feature Importances
1. **`days_in_storage`** (**53.6%**): Primary driver of perishable economic risk.
2. **`net_earning`** (**25.6%**): Spot price margin vs. holding opportunity cost.
3. **`perishability`** (**17.0%**): Crop biological shelf-life hazard rating.
4. **`distance_km`** (**3.8%**): Transportation freight friction.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Node.js 18+
- Python 3.10+
- MongoDB instance running locally on `mongodb://localhost:27017`

### 2. Python ML Microservice
```bash
cd ml_service
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# (Optional) Set your Gemini API key for dynamic copilot %
$env:GEMINI_API_KEY="your_api_key_here"

# Start ML service on port 8000
uvicorn app:app --reload --port 8000
```

### 3. Node.js Backend Gateway
```bash
cd server
npm install

# Seed the 14 APMC Mandis and initial market price matrix
node seed.js

# Start server on port 5000
npm start
```

### 4. React Client UI
```bash
cd client
npm install
npm run dev
# Open http://localhost:5173
```

---

## 📜 License
MIT License. Created by [Ved Jain](https://github.com/Ved-jain).
