"""
Google Gemini AI Agri-Financial Copilot
=======================================
Combines Random Forest deterministic risk probabilities with Google Gemini LLM
to predict fine-tuned continuous liquidation percentages (e.g. 35%, 65%, 80%)
and trader negotiation strategy for Indian APMC mandis.
"""

import os
import json
import re

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Support official google-genai SDK
try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def get_fallback_copilot_advice(net_earning: float, distance_km: float, 
                                perishability: float, days_in_storage: float,
                                rf_action: str, rf_confidence: float, 
                                probabilities: dict, crop_name: str = "Crop", 
                                mandi_name: str = "Mandi") -> dict:
    """
    Deterministic rule-based fallback when Gemini API key is missing or offline.
    Interpolates continuous percentage smoothly using Random Forest probabilities.
    """
    prob_sell_100 = probabilities.get("SELL 100%", 0.0)
    prob_sell_50 = probabilities.get("SELL 50%", 0.0)
    prob_hold = probabilities.get("HOLD", 0.0)
    
    if rf_action == "SELL 100%":
        sell_percentage = 100
        urgency = "HIGH"
        tip = f"Critical shelf-life threshold at {mandi_name}. Liquidate full batch immediately to safeguard principal capital."
    elif rf_action == "SELL 50%":
        # Fine-tune percentage between 35% and 75% based on holding vs liquidation pull
        offset = int(round((prob_sell_100 - prob_hold) * 25))
        sell_percentage = max(30, min(75, 50 + offset))
        urgency = "MEDIUM"
        tip = f"Solid net margin at {mandi_name}. Liquidate {sell_percentage}% today to cover transit freight and secure liquidity; hold remainder."
    else:  # HOLD
        sell_percentage = 0 if prob_hold > 0.65 else 10
        urgency = "LOW"
        tip = f"Current net margin after {distance_km:.0f}km transit is suboptimal at {mandi_name}. Retain inventory in storage for price cycle recovery."

    return {
        "sell_percentage": sell_percentage,
        "copilot_tip": tip,
        "urgency": urgency,
        "copilot_enabled": False
    }

def generate_copilot_advice(net_earning: float, distance_km: float, 
                            perishability: float, days_in_storage: float,
                            rf_action: str, rf_confidence: float, 
                            probabilities: dict, crop_name: str = "Crop", 
                            mandi_name: str = "Mandi") -> dict:
    """
    Prompts Gemini API using Random Forest inputs to synthesize continuous selling %
    and actionable mandi trading advice.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    # If no Gemini API key or SDK missing, use smooth deterministic fallback
    if not api_key or not HAS_GENAI:
        return get_fallback_copilot_advice(
            net_earning, distance_km, perishability, days_in_storage,
            rf_action, rf_confidence, probabilities, crop_name, mandi_name
        )
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""You are an expert Indian Agri-Logistics & APMC Mandi Trading Financial Copilot.
A validated Random Forest model has calculated the following deterministic outputs:
- Crop: {crop_name}
- Target APMC Mandi: {mandi_name}
- True Net Margin: Rs. {net_earning:.2f} / quintal
- Transit Distance: {distance_km:.1f} km
- Perishability Index: {perishability:.0f} / 10
- Days in Storage: {days_in_storage:.0f} days
- Machine Learning Recommended Action: {rf_action} (Confidence: {rf_confidence * 100:.1f}%)
- Model Class Probabilities:
  * HOLD: {probabilities.get('HOLD', 0.0):.3f}
  * SELL 50%: {probabilities.get('SELL 50%', 0.0):.3f}
  * SELL 100%: {probabilities.get('SELL 100%', 0.0):.3f}

Tasks:
1. Determine an exact continuous liquidation percentage (integer between 0 and 100, e.g. 15, 35, 65, 80) that best balances cash flow against decay hazard. Align with the ML action (e.g. if HOLD, 0-20%; if SELL 50%, 35-70%; if SELL 100%, 80-100%).
2. Provide a 1-2 sentence tactical negotiation or truck dispatch tip for the farmer trading at this specific mandi.
3. Provide Urgency: 'LOW', 'MEDIUM', or 'HIGH'.

Respond ONLY in valid raw JSON with this exact structure:
{{
  "sell_percentage": 65,
  "copilot_tip": "string",
  "urgency": "string"
}}"""

        # Try available production models
        models_to_try = ["gemini-3-flash-preview", "gemini-flash-latest", "gemini-2.5-flash"]
        response = None
        
        for m_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=m_name,
                    contents=prompt
                )
                if response and response.text:
                    break
            except Exception:
                continue
                
        if not response or not response.text:
            raise RuntimeError("Gemini models could not be reached.")

        text = response.text.strip()

        
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n", "", text)
            text = re.sub(r"\n```$", "", text)
            
        data = json.loads(text)
        sell_pct = int(data.get("sell_percentage", 50))
        sell_pct = max(0, min(100, sell_pct))
        tip = str(data.get("copilot_tip", "")).strip()
        urgency = str(data.get("urgency", "MEDIUM")).upper()
        
        return {
            "sell_percentage": sell_pct,
            "copilot_tip": tip,
            "urgency": urgency,
            "copilot_enabled": True
        }
    except Exception as e:
        # Fallback on rate-limit, network error, or invalid key
        advice = get_fallback_copilot_advice(
            net_earning, distance_km, perishability, days_in_storage,
            rf_action, rf_confidence, probabilities, crop_name, mandi_name
        )
        return advice
