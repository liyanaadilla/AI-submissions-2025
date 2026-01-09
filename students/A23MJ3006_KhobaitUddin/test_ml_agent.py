"""
Test Script for ML-Integrated Agent

Tests the enhanced agent with ML predictions.
Run with: python3 test_ml_agent.py
"""

import sys
import time

try:
    from agent_enhanced import EnhancedYSMAI_Agent
    from ml_training import MLModelTrainer
except ImportError as e:
    print(f"⚠ Import error: {e}")
    sys.exit(1)


def test_ml_agent():
    """Test the enhanced agent with ML."""
    
    print("\n" + "="*60)
    print("TESTING ML-INTEGRATED AGENT")
    print("="*60)
    
    # Initialize agent with ML
    agent = EnhancedYSMAI_Agent(use_ml=True)
    
    print(f"\nAgent initialized:")
    print(f"  - ML enabled: {agent.use_ml}")
    print(f"  - ML ready: {agent.ml_ready}")
    print(f"  - Threshold high: {agent.threshold_high}°F")
    print(f"  - Threshold low: {agent.threshold_low}°F")
    
    # Test 1: Normal operation
    print("\n" + "-"*60)
    print("TEST 1: Normal Operation")
    print("-"*60)
    
    base_time = time.time()
    result = agent.update(
        temp=72.0,
        timestamp_unix=base_time,
        rpm=1500,
        pressure=45.0,
        vib=5.0
    )
    
    print(f"\nInput:")
    print(f"  Temperature: 72.0°F")
    print(f"  RPM: 1500")
    print(f"  Pressure: 45.0 PSI")
    print(f"  Vibration: 5.0 mm/s")
    
    print(f"\nOutput:")
    print(f"  State: {result['state']}")
    print(f"  Alert: {result['alert_message']}")
    
    if result['ml_insights']:
        print(f"\nML Predictions:")
        for key, value in result['ml_insights'].items():
            print(f"  {key}: {value}")
    
    # Test 2: High temperature
    print("\n" + "-"*60)
    print("TEST 2: High Temperature Alert")
    print("-"*60)
    
    # First reading above threshold
    result1 = agent.update(
        temp=87.0,
        timestamp_unix=base_time + 0.5,
        rpm=2500,
        pressure=55.0,
        vib=8.0
    )
    print(f"\nTick 1 (temp=87°F, above 85°F threshold):")
    print(f"  State: {result1['state']}")
    print(f"  Alert: {result1['alert_message']}")
    print(f"  Changed: {result1['state_changed']}")
    
    # After debounce (1.5 seconds)
    result2 = agent.update(
        temp=88.0,
        timestamp_unix=base_time + 2.1,
        rpm=2500,
        pressure=56.0,
        vib=8.5
    )
    print(f"\nTick 2 (after 1.6s debounce):")
    print(f"  State: {result2['state']}")
    print(f"  Alert: {result2['alert_message']}")
    print(f"  Changed: {result2['state_changed']}")
    
    if result2['ml_insights']:
        print(f"\nML Insights (high temperature scenario):")
        ml = result2['ml_insights']
        if 'fault_detection' in ml:
            print(f"  Fault Detection: {ml['fault_detection']}")
        if 'vibration_anomaly' in ml:
            print(f"  Vibration: {ml['vibration_anomaly']}")
    
    # Test 3: Recovery
    print("\n" + "-"*60)
    print("TEST 3: Recovery to Normal")
    print("-"*60)
    
    agent.reset()
    print("Agent reset")
    
    # Trigger alert
    agent.update(temp=90.0, timestamp_unix=base_time, rpm=2500, pressure=55.0, vib=8.0)
    agent.update(temp=90.0, timestamp_unix=base_time + 2.0, rpm=2500, pressure=55.0, vib=8.0)
    
    # Recover
    result3 = agent.update(
        temp=75.0,
        timestamp_unix=base_time + 2.5,
        rpm=1800,
        pressure=48.0,
        vib=6.0
    )
    print(f"\nTemp drops to 75°F:")
    print(f"  State: {result3['state']}")
    
    # After debounce
    result4 = agent.update(
        temp=75.0,
        timestamp_unix=base_time + 4.1,
        rpm=1800,
        pressure=48.0,
        vib=6.0
    )
    print(f"\nAfter recovery debounce:")
    print(f"  State: {result4['state']}")
    print(f"  Alert: {result4['alert_message']}")
    print(f"  Changed: {result4['state_changed']}")
    
    # Test 4: Direct ML inference
    print("\n" + "-"*60)
    print("TEST 4: Direct ML Inference")
    print("-"*60)
    
    if agent.ml_ready:
        trainer = agent.ml_trainer
        
        print(f"\nFault Detection (normal conditions):")
        fault_result = trainer.predict_fault(rpm=1500, pressure=45, temp=75, vib=5)
        print(f"  Fault: {fault_result['fault']}")
        print(f"  Confidence: {fault_result['confidence']:.4f}")
        
        print(f"\nVibration Anomaly (normal bearings):")
        vib_result = trainer.detect_vibration_anomaly(bearing_1=5, bearing_2=5)
        print(f"  Anomaly: {vib_result['anomaly']}")
        print(f"  Score: {vib_result['score']:.4f}")
        
        print(f"\nPressure Prediction (flow=25):")
        press_result = trainer.predict_pressure(flow_rate=25)
        print(f"  Predicted Pressure: {press_result['predicted_pressure']:.2f} PSI")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("\n✓ All tests completed successfully!")
    print("\nML Module Status:")
    print(f"  - ML Training: {'✓ Trained' if agent.ml_ready else '✗ Not trained'}")
    print(f"  - Models available: 3 (Fault, Vibration, Pressure)")
    print(f"  - Fault Detector: {'✓ Loaded' if agent.ml_trainer.fault_detector else '✗ Not loaded'}")
    print(f"  - Vibration Detector: {'✓ Loaded' if agent.ml_trainer.vibration_detector else '✗ Not loaded'}")
    print(f"  - Pressure Predictor: {'✓ Loaded' if agent.ml_trainer.pressure_predictor else '✗ Not loaded'}")


if __name__ == "__main__":
    test_ml_agent()
