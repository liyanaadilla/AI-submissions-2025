"""
Sample Data Generator

Generates sample simulation output for UI testing and validation.
Produces three JSON files representing different scenarios.
"""

import json
import os
from typing import List, Dict, Any
from controller import SimulationController


def generate_normal_run_100_ticks() -> List[Dict[str, Any]]:
    """
    Generate normal operation scenario: 100 ticks with stable temperatures.
    
    Returns:
        List of 100 tick responses
    """
    ctrl = SimulationController(
        initial_temp=60.0,
        warmup_duration=5.0,
        drift_rate=0.3,
        threshold_high=85.0,
        threshold_low=50.0,
        debounce_sec=1.5,
        update_interval_sec=0.5,
    )
    
    data = []
    for _ in range(100):
        response = ctrl.tick()
        # Remove debug info for cleaner output
        response_clean = {
            "timestamp": response["timestamp"],
            "temperature": response["temperature"],
            "state": response["state"],
            "state_changed": response["state_changed"],
            "alert_message": response["alert_message"],
            "scheduled_tasks": response["scheduled_tasks"],
            "simulation_time": response["simulation_time"],
        }
        data.append(response_clean)
    
    return data


def generate_alert_scenario_100_ticks() -> List[Dict[str, Any]]:
    """
    Generate alert scenario: triggers high/low alerts with recovery.
    
    Returns:
        List of 100 tick responses
    """
    ctrl = SimulationController(
        initial_temp=75.0,
        warmup_duration=3.0,
        drift_rate=1.0,  # Faster drift to trigger alerts
        threshold_high=85.0,
        threshold_low=55.0,
        debounce_sec=1.5,
        update_interval_sec=0.5,
    )
    
    data = []
    for i in range(100):
        response = ctrl.tick()
        response_clean = {
            "timestamp": response["timestamp"],
            "temperature": response["temperature"],
            "state": response["state"],
            "state_changed": response["state_changed"],
            "alert_message": response["alert_message"],
            "scheduled_tasks": response["scheduled_tasks"],
            "simulation_time": response["simulation_time"],
        }
        data.append(response_clean)
        
        # Reverse drift direction at midpoint to trigger recovery
        if i == 50:
            ctrl.simulator.drift_direction *= -1
    
    return data


def generate_fault_injection_50_ticks() -> List[Dict[str, Any]]:
    """
    Generate fault injection scenario: rapid oscillations with fault enabled.
    
    Returns:
        List of 50 tick responses
    """
    ctrl = SimulationController(
        initial_temp=70.0,
        warmup_duration=2.0,
        drift_rate=0.5,
        threshold_high=85.0,
        threshold_low=55.0,
        debounce_sec=1.5,
        update_interval_sec=0.5,
    )
    
    # Enable fault injection after warmup
    data = []
    for i in range(50):
        # Enable fault injection after tick 5 (warmup complete)
        if i == 5:
            ctrl.set_fault_injection(enabled=True, magnitude=12.0)
        
        response = ctrl.tick()
        response_clean = {
            "timestamp": response["timestamp"],
            "temperature": response["temperature"],
            "state": response["state"],
            "state_changed": response["state_changed"],
            "alert_message": response["alert_message"],
            "scheduled_tasks": response["scheduled_tasks"],
            "simulation_time": response["simulation_time"],
        }
        data.append(response_clean)
    
    return data


def save_sample_data(output_dir: str = ".") -> None:
    """
    Generate and save all sample data files.
    
    Args:
        output_dir: Directory to save sample files (default: current directory)
    """
    # Create samples directory if needed
    samples_dir = os.path.join(output_dir, "samples")
    os.makedirs(samples_dir, exist_ok=True)
    
    print("Generating sample data...")
    
    # Generate and save normal run
    print("  - Normal operation (100 ticks)...", end="", flush=True)
    normal_data = generate_normal_run_100_ticks()
    normal_path = os.path.join(samples_dir, "normal_run_100_ticks.json")
    with open(normal_path, "w") as f:
        json.dump(normal_data, f, indent=2)
    print(f" done ({len(normal_data)} ticks)")
    
    # Generate and save alert scenario
    print("  - Alert scenario (100 ticks)...", end="", flush=True)
    alert_data = generate_alert_scenario_100_ticks()
    alert_path = os.path.join(samples_dir, "alert_scenario_100_ticks.json")
    with open(alert_path, "w") as f:
        json.dump(alert_data, f, indent=2)
    print(f" done ({len(alert_data)} ticks)")
    
    # Generate and save fault injection
    print("  - Fault injection (50 ticks)...", end="", flush=True)
    fault_data = generate_fault_injection_50_ticks()
    fault_path = os.path.join(samples_dir, "fault_injection_50_ticks.json")
    with open(fault_path, "w") as f:
        json.dump(fault_data, f, indent=2)
    print(f" done ({len(fault_data)} ticks)")
    
    print("\nSample data generation complete!")
    print(f"Files saved to: {samples_dir}/")
    
    # Print summary statistics
    print("\n=== SAMPLE DATA SUMMARY ===")
    print(f"Normal run:")
    print(f"  Temp range: {min(t['temperature'] for t in normal_data):.1f}°F - {max(t['temperature'] for t in normal_data):.1f}°F")
    print(f"  State changes: {sum(1 for t in normal_data if t['state_changed'])}")
    
    print(f"\nAlert scenario:")
    print(f"  Temp range: {min(t['temperature'] for t in alert_data):.1f}°F - {max(t['temperature'] for t in alert_data):.1f}°F")
    print(f"  State changes: {sum(1 for t in alert_data if t['state_changed'])}")
    
    print(f"\nFault injection:")
    print(f"  Temp range: {min(t['temperature'] for t in fault_data):.1f}°F - {max(t['temperature'] for t in fault_data):.1f}°F")
    print(f"  State changes: {sum(1 for t in fault_data if t['state_changed'])}")


if __name__ == "__main__":
    save_sample_data()
