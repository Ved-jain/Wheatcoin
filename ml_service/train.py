"""
Explainable Agri-Logistics & Liquidation Model Trainer
Trains an ensemble Random Forest model with Stratified 80/20 validation,
5-fold Cross-Validation, and exports full empirical performance metrics.
"""

import os
import json
import pickle
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from dataset_generator import generate_agricultural_dataset

FEATURE_NAMES = ['net_earning', 'distance_km', 'perishability', 'days_in_storage']
CLASS_NAMES = ['HOLD', 'SELL 50%', 'SELL 100%']

def train_and_evaluate():
    print("==================================================")
    print("  KisanMandi Explainable ML Training & Validation")
    print("==================================================")
    
    # 1. Load or Generate Dataset
    csv_path = "agricultural_mandi_dataset.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"Loaded existing dataset: {len(df)} records from {csv_path}")
    else:
        print("Generating new realistic agricultural dataset (3,500 samples)...")
        df = generate_agricultural_dataset(3500)
        df.to_csv(csv_path, index=False)
        
    X = df[FEATURE_NAMES]
    y = df['action']
    
    # 2. Stratified 80/20 Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\nTraining set size: {len(X_train)} | Holdout test set size: {len(X_test)}")
    
    # 3. Model Definition: Explainable Random Forest with depth & leaf limits to prevent overfitting
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=7,
        min_samples_split=8,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
    
    # 4. 5-Fold Stratified Cross-Validation on Training Set
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
    print(f"\n5-Fold Cross-Validation Scores: {[round(s, 4) for s in cv_scores]}")
    print(f"Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # 5. Fit model on full training set
    model.fit(X_train, y_train)
    
    # 6. Evaluate on Unseen Holdout Test Set
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    test_accuracy = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    report_dict = classification_report(y_test, y_pred, target_names=CLASS_NAMES, output_dict=True)
    report_str = classification_report(y_test, y_pred, target_names=CLASS_NAMES)
    
    print("\n---------------- Holdout Test Set Performance ----------------")
    print(f"Test Accuracy:       {test_accuracy * 100:.2f}%")
    print(f"Macro F1-Score:      {f1_macro:.4f}")
    print(f"Weighted F1-Score:   {f1_weighted:.4f}")
    print("\nDetailed Classification Report:")
    print(report_str)
    
    # 7. Feature Importances (Gini Impurity reduction)
    importances = model.feature_importances_
    feat_imp = [
        {"feature": name, "importance": round(float(imp), 4), "percentage": round(float(imp * 100), 1)}
        for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: x[1], reverse=True)
    ]
    
    print("Feature Importances:")
    for item in feat_imp:
        print(f"  - {item['feature']:<18}: {item['percentage']}%")
        
    # 8. Export Artifacts
    os.makedirs('models', exist_ok=True)
    model_path = 'models/recommender.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"\nTrained Model saved to {model_path}")
    
    metrics_data = {
        "model_architecture": "RandomForestClassifier(n_estimators=100, max_depth=7)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "test_accuracy": round(float(test_accuracy), 4),
        "f1_macro": round(float(f1_macro), 4),
        "f1_weighted": round(float(f1_weighted), 4),
        "cv_mean_accuracy": round(float(cv_scores.mean()), 4),
        "cv_std_accuracy": round(float(cv_scores.std()), 4),
        "cv_folds": [round(float(s), 4) for s in cv_scores],
        "feature_importances": feat_imp,
        "confusion_matrix": cm,
        "class_names": CLASS_NAMES,
        "classification_report": report_dict,
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    metrics_path = 'models/model_metrics.json'
    with open(metrics_path, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Validation Metrics & Proof saved to {metrics_path}")
    print("==================================================\n")

if __name__ == "__main__":
    train_and_evaluate()
