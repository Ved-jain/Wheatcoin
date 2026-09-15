"""
Model Training & 5-Fold Stratified Cross-Validation Engine
"""

import os
import json
import pickle
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from .config import FEATURE_NAMES, CLASS_NAMES

def train_and_evaluate_model(df: pd.DataFrame, export_models: bool = True) -> tuple:
    """
    Trains explainable Random Forest with 5-Fold Stratified Cross-Validation
    and exports production artifacts.
    """
    X = df[FEATURE_NAMES]
    y = df['action']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=7,
        min_samples_split=8,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
    
    # 5-Fold Stratified Cross-Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
    
    # Fit model on training set
    model.fit(X_train, y_train)
    
    # Evaluation on holdout test set
    y_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    report_dict = classification_report(y_test, y_pred, target_names=CLASS_NAMES, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    # Feature Importances (Gini impurity reduction)
    importances = model.feature_importances_
    feat_imp = [
        {"feature": name, "importance": round(float(imp), 4), "percentage": round(float(imp * 100), 1)}
        for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: x[1], reverse=True)
    ]
    
    metrics_data = {
        "model_architecture": "RandomForestClassifier(n_estimators=100, max_depth=7)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "test_accuracy": round(float(test_acc), 4),
        "f1_macro": round(float(f1_macro), 4),
        "f1_weighted": round(float(f1_weighted), 4),
        "cv_mean_accuracy": round(float(cv_scores.mean()), 4),
        "cv_std_accuracy": round(float(cv_scores.std()), 4),
        "cv_folds": [round(float(s), 4) for s in cv_scores],
        "feature_importances": feat_imp,
        "confusion_matrix": cm,
        "class_names": CLASS_NAMES,
        "classification_report": report_dict,
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_source": "Real Agmarknet Mandi Data (Data.gov.in)"
    }
    
    if export_models:
        os.makedirs('models', exist_ok=True)
        model_path = 'models/recommender.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
            
        metrics_path = 'models/model_metrics.json'
        with open(metrics_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)
            
    return model, metrics_data
