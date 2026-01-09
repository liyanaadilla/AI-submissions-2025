#!/usr/bin/env python3
"""
Complete Integration Example - YSMAI with Kaggle-Trained Models

This example shows how to use the complete YSMAI system:
1. Initialize the enhanced agent (with Kaggle-trained models)
2. Simulate sensor readings
3. Get FSM state + ML predictions
4. Detect faults and anomalies
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_enhanced import EnhancedYSMAI_Agent
from controller import SimulationController
from simulator import TemperatureSimulator


def example_1_basic_usage():
    """Example 1: Basic agent usage with ML"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Enhanced Agent Usage")
    print("="*70)
    
    # Initialize agent with Kaggle-trained models
    agent = EnhancedYSMAI_Agent(use_ml=True, threshold_high=85, threshold_low=50)
    
    print(f"\nAgent initialized:")
    print(f"  State: {agent.get_state()}")
    print(f"  ML Enabled: True")
    print(f"  Thresholds: {agent.threshold_low}°F - {agent.threshold_high}°F")
    
    # Simulate normal operation
    print(f"\n--- Normal Operation (72°F) ---")
    result = agent.update(
        temp=72.0,
        timestamp_unix=1000.0,
        rpm=2000,
        pressure=50,
        vib=5.0
    )
    
    print(f"State: {result['state']}")
    print(f"Temperature: {result['temperature']}°F")
    print(f"Alert: {result['alert_message']}")
    
    if result['ml_insights']:
        insights = result['ml_insights']
        fault = insights.get('fault_detection', {})
        vibration = insights.get('vibration_anomaly', {})
        pressure = insights.get('pressure_prediction', {})
        
        print(f"\nML Insights:")
        print(f"  Fault Detection: {fault.get('detected')} (confidence: {fault.get('confidence', 0):.2%})")
        print(f"  Vibration Anomaly: {vibration.get('detected')} (score: {vibration.get('score', 0):.2f})")
        print(f"  Pressure Prediction: {pressure.get('predicted_pressure', 0):.1f} PSI")


def example_2_fault_detection():
    """Example 2: Detecting high temperature with ML"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Fault Detection - High Temperature")
    print("="*70)
    
    agent = EnhancedYSMAI_Agent(use_ml=True, threshold_high=85, debounce_sec=1.0)
    
    print(f"\n--- Scenario: Temperature rises above threshold ---")
    
    # Simulate temperature rise
    for i, temp in enumerate([72, 80, 88, 92, 95]):
        timestamp = 1000.0 + i
        
        result = agent.update(
            temp=temp,
            timestamp_unix=timestamp,
            rpm=2500,
            pressure=55,
            vib=8.0
        )
        
        print(f"\nTick {i+1} (T={temp}°F):")
        print(f"  State: {result['state']}")
        print(f"  Alert: {result['alert_message']}")
        
        if result['ml_insights']:
            fault = result['ml_insights'].get('fault_detection', {})
            if fault.get('detected'):
                print(f"  ⚠️  ML ALERT: Fault detected (confidence: {fault.get('confidence', 0):.2%})")


def example_3_anomaly_detection():
    """Example 3: Vibration anomaly detection"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Anomaly Detection - Vibration")
    print("="*70)
    
    agent = EnhancedYSMAI_Agent(use_ml=True)
    
    print(f"\n--- Scenario: Normal vs Abnormal Vibration ---")
    
    test_cases = [
        ("Normal vibration", 5.0),
        ("Slightly elevated", 15.0),
        ("High vibration (anomaly)", 35.0),
    ]
    
    for desc, vib in test_cases:
        result = agent.update(
            temp=72.0,
            timestamp_unix=1000.0,
            rpm=2000,
            pressure=50,
            vib=vib
        )
        
        print(f"\n{desc} (Vib={vib} mm/s):")
        if result['ml_insights']:
            vibration = result['ml_insights'].get('vibration_anomaly', {})
            anomaly_detected = vibration.get('detected', False)
            score = vibration.get('score', 0)
            
            print(f"  Anomaly Detected: {anomaly_detected}")
            print(f"  Anomaly Score: {score:.2f}")
            
            if anomaly_detected:
                print(f"  ⚠️  ALERT: Abnormal vibration pattern detected!")


def example_4_pressure_prediction():
    """Example 4: Pressure prediction"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Pressure Prediction")
    print("="*70)
    
    from ml_training_kaggle import MLModelTrainer
    
    print(f"\n--- Predicting Expected Pressure at Different Flow Rates ---")
    
    trainer = MLModelTrainer()
    if trainer.load_all_models():
        flow_rates = [10, 20, 30, 40, 50]
        
        for flow_rate in flow_rates:
            prediction = trainer.predict_pressure(flow_rate)
            predicted_psi = prediction.get('predicted_pressure', 0)
            
            print(f"\nFlow Rate: {flow_rate} GPM")
            print(f"  Predicted Pressure: {predicted_psi:.1f} PSI")


def example_5_full_simulation():
    """Example 5: Full simulation with controller"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Full Simulation with SimulationController")
    print("="*70)
    
    # Create controller (uses original agent)
    controller = SimulationController()
    
    print(f"\n--- Running 10-second simulation ---")
    
    # Simulate 10 ticks (10 seconds)
    results = []
    for i in range(10):
        result = controller.tick()
        results.append(result)
        
        print(f"\nTick {i+1}:")
        print(f"  Temperature: {result['temperature']:.1f}°F")
        print(f"  State: {result['state']}")
        
        if result['alert_message']:
            print(f"  Alert: {result['alert_message']}")
    
    # Summary
    print(f"\n--- Simulation Summary ---")
    normal_count = sum(1 for r in results if r['state'] == 'NORMAL')
    alert_count = sum(1 for r in results if 'ALERT' in r['state'])
    
    print(f"Ticks: {len(results)}")
    print(f"Normal State: {normal_count}")
    print(f"Alert State: {alert_count}")


def example_6_ml_only_comparison():
    """Example 6: Compare FSM vs FSM+ML"""
    print("\n" + "="*70)
    print("EXAMPLE 6: FSM vs FSM+ML Comparison")
    print("="*70)
    
    # FSM only (original agent)
    from agent import YSMAI_Agent
    fsm_agent = YSMAI_Agent(threshold_high=85)
    
    # FSM + ML (enhanced agent)
    ml_agent = EnhancedYSMAI_Agent(use_ml=True, threshold_high=85)
    
    print(f"\n--- Testing: Normal temperature with high vibration ---")
    
    test_data = {
        'temp': 75.0,
        'timestamp_unix': 1000.0,
        'rpm': 2500,
        'pressure': 55,
        'vib': 35.0  # High vibration = potential bearing fault
    }
    
    print(f"Sensor Data:")
    print(f"  Temperature: {test_data['temp']}°F")
    print(f"  Vibration: {test_data['vib']} mm/s")
    print(f"  RPM: {test_data['rpm']}")
    print(f"  Pressure: {test_data['pressure']} PSI")
    
    # FSM-only response
    fsm_result = fsm_agent.update(test_data['temp'], test_data['timestamp_unix'])
    print(f"\nFSM-Only Decision:")
    print(f"  State: {fsm_result['state']}")
    print(f"  Alert: {fsm_result.get('alert_message', 'None')}")
    print(f"  Reasoning: Temperature is normal (75°F), FSM sees no issue")
    
    # FSM+ML response
    ml_result = ml_agent.update(
        test_data['temp'],
        test_data['timestamp_unix'],
        test_data['rpm'],
        test_data['pressure'],
        test_data['vib']
    )
    print(f"\nFSM+ML Decision:")
    print(f"  State: {ml_result['state']}")
    print(f"  Alert: {ml_result.get('alert_message', 'None')}")
    
    if ml_result['ml_insights']:
        vibration = ml_result['ml_insights'].get('vibration_anomaly', {})
        if vibration.get('detected'):
            print(f"  ML Alert: Vibration anomaly detected!")
            print(f"  Reasoning: High vibration (35 mm/s) = bearing fault risk")
    
    print(f"\n💡 Key Insight:")
    print(f"   FSM checks temperature; ML adds vibration intelligence")
    print(f"   Together they provide comprehensive fault detection")


def main():
    print("\n" + "="*70)
    print("YSMAI SYSTEM - COMPLETE INTEGRATION EXAMPLES")
    print("Kaggle-Trained ML Models")
    print("="*70)
    
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"This script demonstrates 6 complete usage patterns")
    
    try:
        example_1_basic_usage()
        example_2_fault_detection()
        example_3_anomaly_detection()
        example_4_pressure_prediction()
        example_5_full_simulation()
        example_6_ml_only_comparison()
        
        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70)
        
        print(f"\nNext Steps:")
        print(f"1. Review KAGGLE_INTEGRATION_SUMMARY.txt for details")
        print(f"2. Integrate with Streamlit frontend (Nafis)")
        print(f"3. Deploy to production with Kaggle dataset caching")
        print(f"4. Monitor ML prediction accuracy over time")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
