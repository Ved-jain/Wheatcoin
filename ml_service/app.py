from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np
import os

app = FastAPI(title="KisanMandi AI Microservice")

model = None
MODEL_PATH = "models/recommender.pkl"

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
            print("Advanced Model loaded successfully.")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}. Run train.py first.")

load_model()

class PredictionRequest(BaseModel):
    net_earning: float
    distance_km: float
    perishability: float

@app.get("/")
def read_root():
    return {"status": "AI Microservice is running"}

@app.post("/predict_action")
def predict_action(req: PredictionRequest):
    if model is None:
        return {"error": "Model not loaded. Please run train.py first."}
        
    features = np.array([[req.net_earning, req.distance_km, req.perishability]])
    prediction = model.predict(features)[0]
    
    if prediction == 2:
        action = "SELL 100%"
        reason = "Crop is highly perishable. Sell immediately before freshness drops further."
    elif prediction == 1:
        action = "SELL 50%"
        reason = "Price is good, but market volatility indicates a potential hike. Average out the risk."
    else:
        action = "HOLD"
        reason = "Net earnings are too low and crop can be stored safely. Wait for better rates."
    
    return {
        "net_earning": req.net_earning,
        "distance_km": req.distance_km,
        "recommendation": action,
        "reasoning": reason
    }
