"""
Training Script for YSMAI ML Models

Trains all ML models and generates reports.
Run with: python3 train_models.py
"""

import sys
import os

try:
    from ml_training import MLModelTrainer, ML_AVAILABLE
except ImportError as e:
    print(f"⚠ Import error: {e}")
    print("Make sure ml_training.py is in the same directory")
    sys.exit(1)


def main():
    """Main training routine."""
    
    if not ML_AVAILABLE:
        print("="*60)
        print("ML LIBRARIES NOT AVAILABLE")
        print("="*60)
        print("\nInstall required packages with:")
        print("  pip install pandas scikit-learn numpy")
        print("\nThen run this script again:")
        print("  python3 train_models.py")
        sys.exit(1)
    
    print("\n" + "#"*60)
    print("# YSMAI ML MODEL TRAINING")
    print("# Training 3 models for fault detection and prediction")
    print("#"*60)
    
    # Initialize trainer
    trainer = MLModelTrainer(model_dir="models")
    
    # Train all models
    print("\nStarting training pipeline...")
    results = trainer.train_all_models()
    
    # Print summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    
    for model_name, metrics in results.items():
        print(f"\n✓ {model_name}:")
        
        if 'error' in metrics:
            print(f"  ERROR: {metrics['error']}")
            continue
        
        for key, value in metrics.items():
            if key == 'features':
                print(f"  {key}: {', '.join(value)}")
            elif isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
    
    # Print model locations
    print("\n" + "="*60)
    print("TRAINED MODELS LOCATION")
    print("="*60)
    
    models_dir = trainer.model_dir
    print(f"\nModels saved to: {models_dir}/")
    
    if os.path.exists(models_dir):
        files = os.listdir(models_dir)
        for f in sorted(files):
            filepath = os.path.join(models_dir, f)
            size = os.path.getsize(filepath)
            print(f"  - {f} ({size} bytes)")
    
    # Print usage instructions
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
The trained models are now ready for inference. To use them:

1. In your Python code:
   
   from ml_training import MLModelTrainer
   
   trainer = MLModelTrainer()
   trainer.load_all_models()
   
   # Make predictions
   fault = trainer.predict_fault(rpm=2000, pressure=50, temp=75, vib=10)
   anomaly = trainer.detect_vibration_anomaly(bearing_1=5, bearing_2=5)
   pressure = trainer.predict_pressure(flow_rate=25)

2. Or use the enhanced agent with ML:
   
   from agent_enhanced import EnhancedYSMAI_Agent
   
   agent = EnhancedYSMAI_Agent(use_ml=True)
   result = agent.update(temp=75, timestamp_unix=1000, rpm=2000, 
                         pressure=50, vib=10)

3. To retrain models later:
   
   python3 train_models.py
""")
    
    print("="*60)
    print("✓ TRAINING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
