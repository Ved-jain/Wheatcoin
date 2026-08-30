import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import pickle
import os

def create_mock_data():
    # Target actions: 0 = HOLD, 1 = SELL 50% (Averaging), 2 = SELL 100%
    data = {
        'net_earning': [1500, 2200, 1800, 2500, 1200, 2300, 1600, 2400, 2100, 1900],
        'distance_km': [100,  20,   50,   10,   120,  15,   80,   5,    25,   40],
        'perishability':[1,   2,    8,    9,    1,    2,    7,    8,    2,    1],
        'action':      [0,    1,    2,    2,    0,    1,    2,    2,    1,    0] 
        # Highly perishable + medium/high earning -> SELL 100% (2)
        # Low perishability + medium/high earning -> SELL 50% (1)
        # Low earning -> HOLD (0)
    }
    return pd.DataFrame(data)

def train_model():
    print("Training Advanced Risk-Adjusted Recommender Model...")
    df = create_mock_data()
    
    X = df[['net_earning', 'distance_km', 'perishability']]
    y = df['action']
    
    model = DecisionTreeClassifier(max_depth=4)
    model.fit(X, y)
    
    os.makedirs('models', exist_ok=True)
    with open('models/recommender.pkl', 'wb') as f:
        pickle.dump(model, f)
        
    print("Advanced Model saved to models/recommender.pkl successfully!")

if __name__ == "__main__":
    train_model()
