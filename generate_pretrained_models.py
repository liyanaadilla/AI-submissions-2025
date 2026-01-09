#!/usr/bin/env python3
"""
Generate pre-trained synthetic ML models for YSMAI testing.
This creates pickle files for the three ML models using sklearn.
"""

import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LinearRegression

# Generate training data
def generate_fault_data(n_samples=500):
    """Generate synthetic fault detection training data."""
    X = np.random.rand(n_samples, 4) * np.array([3000, 80, 115, 50])  # RPM, Pressure, Temp, Vib
    # Fault rule: High temp + high vibration = fault
    y = ((X[:, 2] > 90) & (X[:, 3] > 30)).astype(int)
    return X, y

def generate_vibration_data(n_samples=500):
    """Generate synthetic vibration detection training data."""
    # 90% normal, 10% anomalous
    normal_count = int(n_samples * 0.9)
    anomaly_count = n_samples - normal_count
    
    normal_data = np.random.normal(5, 2, (normal_count, 2))
    anomaly_data = np.random.normal(25, 5, (anomaly_count, 2))
    
    return np.vstack([normal_data, anomaly_data])

def generate_pressure_data(n_samples=500):
    """Generate synthetic pressure prediction training data."""
    X = np.random.rand(n_samples, 1) * 50  # Flow rate
    y = 30 + (X.flatten() * 0.8) + np.random.normal(0, 5, n_samples)
    return X, y

# Train and save models
def create_models():
    """Train and save all ML models."""
    models_dir = "/Users/khobaituddinsimran/AI-submissions-2025/models"
    os.makedirs(models_dir, exist_ok=True)
    
    print("=" * 60)
    print("Generating Pre-trained ML Models for YSMAI")
    print("=" * 60)
    
    # 1. Fault Detector (Random Forest)
    print("\n🔧 Training Fault Detector (Random Forest)...")
    X, y = generate_fault_data()
    fault_detector = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    fault_detector.fit(X, y)
    
    fault_path = os.path.join(models_dir, "fault_detector.pkl")
    with open(fault_path, 'wb') as f:
        pickle.dump(fault_detector, f)
    print(f"   ✓ Saved to: {fault_path}")
    print(f"   Accuracy: {fault_detector.score(X, y):.4f}")
    
    # 2. Vibration Detector (Isolation Forest)
    print("\n🔧 Training Vibration Detector (Isolation Forest)...")
    X = generate_vibration_data()
    vibration_detector = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_jobs=-1
    )
    vibration_detector.fit(X)
    
    vibration_path = os.path.join(models_dir, "vibration_detector.pkl")
    with open(vibration_path, 'wb') as f:
        pickle.dump(vibration_detector, f)
    print(f"   ✓ Saved to: {vibration_path}")
    
    # 3. Pressure Predictor (Linear Regression)
    print("\n🔧 Training Pressure Predictor (Linear Regression)...")
    X, y = generate_pressure_data()
    pressure_predictor = LinearRegression()
    pressure_predictor.fit(X, y)
    
    pressure_path = os.path.join(models_dir, "pressure_predictor.pkl")
    with open(pressure_path, 'wb') as f:
        pickle.dump(pressure_predictor, f)
    print(f"   ✓ Saved to: {pressure_path}")
    print(f"   R² Score: {pressure_predictor.score(X, y):.4f}")
    
    print("\n" + "=" * 60)
    print("✓ All models trained and saved successfully!")
    print("=" * 60)
    print("\nModels are now ready for inference:")
    print(f"  • {fault_path}")
    print(f"  • {vibration_path}")
    print(f"  • {pressure_path}")

if __name__ == "__main__":
    create_models()
