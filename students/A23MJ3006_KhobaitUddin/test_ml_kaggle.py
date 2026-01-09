#!/usr/bin/env python3
"""
Test script for ML-enhanced YSMAI Agent with Kaggle-trained models

Verifies:
1. ML models loaded correctly
2. Agent works with and without ML
3. ML predictions generated
4. Graceful fallback working
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_enhanced import EnhancedYSMAI_Agent
from ml_training_kaggle import MLModelTrainer, ML_AVAILABLE


def test_basic_initialization():
    """Test 1: Agent initializes correctly"""
    print("\n" + "="*60)
    print("TEST 1: Agent Initialization")
    print("="*60)
    
    try:
        agent = EnhancedYSMAI_Agent(use_ml=True)
        print("✓ Enhanced agent initialized with ML=True")
        print(f"  State: {agent.get_state()}")
        print(f"  ML Available: {ML_AVAILABLE}")
        print(f"  ML Ready: {agent.ml_ready}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return False


def test_normal_operation():
    """Test 2: Normal operation without alerts"""
    print("\n" + "="*60)
    print("TEST 2: Normal Operation")
    print("="*60)
    
    agent = EnhancedYSMAI_Agent(use_ml=True)
    
    # Simulate 5 ticks of normal operation
    for i in range(5):
        result = agent.update(
            temp=72.0,
            timestamp_unix=1000.0 + i,
            rpm=2000,
            pressure=50,
            vib=5.0
        )
        
        print(f"\nTick {i+1}:")
        print(f"  State: {result['state']}")
        print(f"  Temp: {result['temperature']}°F")
        print(f"  Alert: {result['alert_message']}")
        
        if result['ml_insights']:
            print(f"  ML Fault: {result['ml_insights'].get('fault_detection', {}).get('detected', 'N/A')}")
            print(f"  ML Vibration Anomaly: {result['ml_insights'].get('vibration_anomaly', {}).get('detected', 'N/A')}")
    
    if agent.get_state() == "NORMAL":
        print("\n✓ Normal operation working correctly")
        return True
    else:
        print(f"\n✗ Expected NORMAL state, got {agent.get_state()}")
        return False


def test_high_temp_alert():
    """Test 3: High temperature alert with debounce"""
    print("\n" + "="*60)
    print("TEST 3: High Temperature Alert")
    print("="*60)
    
    agent = EnhancedYSMAI_Agent(use_ml=True, threshold_high=85.0, debounce_sec=1.5)
    
    # First tick: high temp (within debounce window)
    result1 = agent.update(
        temp=90.0,
        timestamp_unix=1000.0,
        rpm=2000,
        pressure=50,
        vib=5.0
    )
    print(f"\nTick 1 (T=1000.0): Temp=90°F")
    print(f"  State: {result1['state']} (debounce window)")
    
    # Wait for debounce to expire
    result2 = agent.update(
        temp=90.0,
        timestamp_unix=1001.6,  # 1.6 seconds later
        rpm=2000,
        pressure=50,
        vib=5.0
    )
    print(f"\nTick 2 (T=1001.6): Temp=90°F (debounce expired)")
    print(f"  State: {result2['state']}")
    print(f"  Alert: {result2['alert_message']}")
    
    if result2['state'] == "ALERT_HIGH":
        print("\n✓ High temperature alert working correctly")
        return True
    else:
        print(f"\n✗ Expected ALERT_HIGH state, got {result2['state']}")
        return False


def test_recovery():
    """Test 4: Recovery from alert to normal"""
    print("\n" + "="*60)
    print("TEST 4: Recovery from Alert")
    print("="*60)
    
    agent = EnhancedYSMAI_Agent(use_ml=True, threshold_high=85.0, debounce_sec=1.5)
    
    # Trigger alert
    agent.update(temp=90.0, timestamp_unix=1000.0, rpm=2000, pressure=50, vib=5.0)
    agent.update(temp=90.0, timestamp_unix=1001.6, rpm=2000, pressure=50, vib=5.0)
    print(f"Initial state: {agent.get_state()}")
    
    # Temperature drops
    result = agent.update(
        temp=72.0,
        timestamp_unix=1002.0,
        rpm=2000,
        pressure=50,
        vib=5.0
    )
    print(f"\nTemperature drops to 72°F")
    print(f"State: {result['state']} (in debounce window)")
    
    # Wait for debounce
    result = agent.update(
        temp=72.0,
        timestamp_unix=1003.6,
        rpm=2000,
        pressure=50,
        vib=5.0
    )
    print(f"\nAfter debounce expires:")
    print(f"State: {result['state']}")
    print(f"Alert: {result['alert_message']}")
    
    if result['state'] == "NORMAL":
        print("\n✓ Recovery working correctly")
        return True
    else:
        print(f"\n✗ Expected NORMAL state, got {result['state']}")
        return False


def test_ml_inference():
    """Test 5: Direct ML inference with Kaggle models"""
    print("\n" + "="*60)
    print("TEST 5: ML Inference with Kaggle Models")
    print("="*60)
    
    if not ML_AVAILABLE:
        print("⚠️  ML not available, skipping this test")
        return True
    
    try:
        trainer = MLModelTrainer()
        
        # Test loading models
        if trainer.load_all_models():
            print("✓ Models loaded successfully")
            
            # Test fault detection
            fault = trainer.predict_fault(rpm=2000, pressure=50, temp=75, vib=10)
            print(f"  Fault Detection: {fault.get('detected', 'N/A')} (confidence: {fault.get('confidence', 0):.2f})")
            
            # Test vibration anomaly
            anomaly = trainer.detect_vibration_anomaly(bearing_1=5, bearing_2=5)
            print(f"  Vibration Anomaly: {anomaly.get('detected', 'N/A')} (score: {anomaly.get('score', 0):.2f})")
            
            # Test pressure prediction
            pressure = trainer.predict_pressure(flow_rate=25)
            print(f"  Pressure Prediction: {pressure.get('predicted_pressure', 0):.2f} PSI")
            
            print("\n✓ ML inference working correctly")
            return True
        else:
            print("⚠️  Could not load trained models")
            return False
    
    except Exception as e:
        print(f"✗ ML inference failed: {e}")
        return False


def test_without_ml():
    """Test 6: Agent works without ML"""
    print("\n" + "="*60)
    print("TEST 6: Agent Without ML (Fallback)")
    print("="*60)
    
    agent = EnhancedYSMAI_Agent(use_ml=False)
    
    result = agent.update(
        temp=75.0,
        timestamp_unix=1000.0,
        rpm=2000,
        pressure=50,
        vib=5.0
    )
    
    print(f"State: {result['state']}")
    print(f"ML Insights: {result['ml_insights']}")
    
    if result['state'] == "NORMAL" and result['ml_insights'] is None:
        print("\n✓ Fallback mode working correctly (FSM only, no ML)")
        return True
    else:
        print("\n✗ Fallback mode failed")
        return False


def test_training_report():
    """Test 7: Check training report"""
    print("\n" + "="*60)
    print("TEST 7: Training Report")
    print("="*60)
    
    import json
    
    report_path = "models/training_report.json"
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        print(f"Training timestamp: {report.get('timestamp', 'N/A')}")
        print(f"Kaggle available: {report.get('kaggle_available', 'N/A')}")
        
        results = report.get('results', {})
        if 'fault_detector' in results:
            fd = results['fault_detector']
            print(f"\nFault Detector (Random Forest):")
            print(f"  Training Accuracy: {fd.get('train_accuracy', 'N/A'):.4f}")
            print(f"  Testing Accuracy: {fd.get('test_accuracy', 'N/A'):.4f}")
        
        if 'pressure_predictor' in results:
            pp = results['pressure_predictor']
            print(f"\nPressure Predictor (Linear Regression):")
            print(f"  Training R²: {pp.get('train_r2', 'N/A'):.4f}")
            print(f"  Testing R²: {pp.get('test_r2', 'N/A'):.4f}")
            print(f"  Testing RMSE: {pp.get('test_rmse', 'N/A'):.2f} PSI")
        
        print("\n✓ Training report valid")
        return True
    else:
        print(f"✗ Training report not found at {report_path}")
        return False


def main():
    print("\n" + "="*60)
    print("YSMAI Enhanced Agent Tests - Kaggle Datasets")
    print("="*60)
    
    tests = [
        ("Basic Initialization", test_basic_initialization),
        ("Normal Operation", test_normal_operation),
        ("High Temperature Alert", test_high_temp_alert),
        ("Recovery from Alert", test_recovery),
        ("ML Inference", test_ml_inference),
        ("Fallback Without ML", test_without_ml),
        ("Training Report", test_training_report),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, passed_test in results:
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
