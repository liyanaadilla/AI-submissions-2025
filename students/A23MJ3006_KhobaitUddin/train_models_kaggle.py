#!/usr/bin/env python3
"""
YSMAI ML Training Script - Kaggle Datasets Edition

Trains all 3 ML models using real Kaggle datasets:
1. Engine Fault Detection Data
2. NASA Bearing Dataset  
3. Hydraulic Systems Condition Monitoring

Usage:
    python train_models_kaggle.py

First run:
- Downloads datasets from Kaggle (1-5 min)
- Trains all 3 models (30-75 sec)
- Saves to models/ directory

Subsequent runs:
- Uses cached datasets
- Trains models (30-75 sec)
- Overwrites previous models

Prerequisites:
- pip install -r requirements.txt
- Kaggle account (free) - datasets are public

Models created:
- models/fault_detector.pkl (Random Forest)
- models/vibration_detector.pkl (Isolation Forest)
- models/pressure_predictor.pkl (Linear Regression)
- models/training_report.json (metrics)
"""

import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_training_kaggle import MLModelTrainer, ML_AVAILABLE

def main():
    if not ML_AVAILABLE:
        print("❌ Error: ML libraries not installed")
        print("Run: pip install -r requirements.txt")
        return 1
    
    trainer = MLModelTrainer()
    
    print("\n" + "="*60)
    print("YSMAI ML Model Training - Real Kaggle Datasets")
    print("="*60 + "\n")
    
    print("This script will:")
    print("1. Download datasets from Kaggle (first time: 1-5 min)")
    print("2. Train 3 ML models (30-75 seconds)")
    print("3. Save models to models/ directory\n")
    
    results = trainer.train_all_models()
    
    if results:
        print("\n✅ Training successful!")
        print("\nModels saved:")
        print("  • models/fault_detector.pkl")
        print("  • models/vibration_detector.pkl")
        print("  • models/pressure_predictor.pkl")
        print("  • models/training_report.json")
        print("\nReady for use with agent_enhanced.py")
        return 0
    else:
        print("\n❌ Training failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
