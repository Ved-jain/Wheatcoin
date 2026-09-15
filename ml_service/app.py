import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np
import json

app = FastAPI(title="KisanMandi Explainable AI Microservice", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
model_metrics = {}
MODEL_PATH = "models/recommender.pkl"
METRICS_PATH = "models/model_metrics.json"

def load_resources():
    global model, model_metrics
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
            print("Random Forest Recommender loaded successfully.")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}. Run train.py first.")

    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, 'r') as f:
            model_metrics = json.load(f)
            print("Model evaluation metrics loaded successfully.")
    else:
        print(f"Warning: Metrics file not found at {METRICS_PATH}.")

load_resources()

from pipeline.gemini_copilot import generate_copilot_advice

class PredictionRequest(BaseModel):
    net_earning: float
    distance_km: float
    perishability: float
    days_in_storage: float = 0.0
    crop_name: str = "Crop"
    mandi_name: str = "Mandi"

@app.get("/")
def read_root():
    return {
        "service": "KisanMandi Explainable AI Microservice",
        "status": "online",
        "model_loaded": model is not None,
        "metrics_loaded": bool(model_metrics),
        "gemini_copilot": bool(os.environ.get("GEMINI_API_KEY"))
    }

@app.get("/model_metrics")
def get_model_metrics():
    if not model_metrics:
        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH, 'r') as f:
                return json.load(f)
        return {"error": "Metrics not yet computed. Run train.py."}
    return model_metrics

@app.post("/predict_action")
def predict_action(req: PredictionRequest):
    if model is None:
        return {"error": "Model not loaded. Please run train.py first."}
        
    features = np.array([[req.net_earning, req.distance_km, req.perishability, req.days_in_storage]])
    
    # Predict probabilities across classes: 0 = HOLD, 1 = SELL 50%, 2 = SELL 100%
    probs = model.predict_proba(features)[0]
    prediction = int(np.argmax(probs))
    confidence = float(probs[prediction])
    
    prob_dict = {
        "HOLD": round(float(probs[0]), 3),
        "SELL 50%": round(float(probs[1]), 3),
        "SELL 100%": round(float(probs[2]), 3)
    }
    
    # Explainable context generation
    if prediction == 2:
        action = "SELL 100%"
        if req.perishability >= 7 and req.days_in_storage >= 2:
            reason = f"High spoilage hazard ({int(req.days_in_storage)} days stored, perishability {int(req.perishability)}/10). Urgent liquidation recommended to protect principal value."
        elif req.net_earning > 2500:
            reason = f"Exceptional spot price margin (₹{req.net_earning:.0f}/q). Full liquidation recommended to capture peak arbitrage."
        else:
            reason = f"Shelf-life depletion hazard outweighs holding expectation. Immediate liquidation advised."
    elif prediction == 1:
        action = "SELL 50%"
        reason = f"Solid net margin (₹{req.net_earning:.0f}/q) with manageable decay risk. Staggered partial liquidation locks in cash flow while hedging against future price spikes."
    else:
        action = "HOLD"
        if req.perishability <= 4 and req.days_in_storage <= 15:
            reason = f"Durable crop with minimal spoilage hazard. Net margins are currently suboptimal; hold in storage for price cycle recovery."
        else:
            reason = f"Net earning after {req.distance_km:.0f}km transit does not cover target threshold. Retain inventory."
            
    # Invoke Gemini AI Copilot (calculating continuous liquidation % and tactical trader advice)
    copilot = generate_copilot_advice(
        net_earning=req.net_earning,
        distance_km=req.distance_km,
        perishability=req.perishability,
        days_in_storage=req.days_in_storage,
        rf_action=action,
        rf_confidence=confidence,
        probabilities=prob_dict,
        crop_name=req.crop_name,
        mandi_name=req.mandi_name
    )
    
    return {
        "net_earning": req.net_earning,
        "distance_km": req.distance_km,
        "perishability": req.perishability,
        "days_in_storage": req.days_in_storage,
        "recommendation": action,
        "confidence": round(confidence, 3),
        "confidence_pct": round(confidence * 100, 1),
        "probabilities": prob_dict,
        "reasoning": reason,
        "sell_percentage": copilot["sell_percentage"],
        "copilot_tip": copilot["copilot_tip"],
        "urgency": copilot["urgency"],
        "copilot_enabled": copilot["copilot_enabled"],
        "model_type": "Hybrid Compound AI (Explainable Random Forest + Gemini Copilot)"
    }

