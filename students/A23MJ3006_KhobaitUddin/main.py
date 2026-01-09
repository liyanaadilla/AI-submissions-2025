#!/usr/bin/env python3
"""
YSMAI HVAC Monitoring System - Main Entry Point

Demonstrates the SimulationController API with a sample 5-minute run.
"""

import json
from controller import SimulationController


def main():
    """Run a demonstration simulation."""
    
    print("=" * 80)
    print("YSMAI HVAC MONITORING SYSTEM - BACKEND DEMO")
    print("=" * 80)
    print()
    
    # Initialize controller with default parameters
    ctrl = SimulationController(
        initial_temp=60.0,
        warmup_duration=5.0,
        drift_rate=0.5,
        threshold_high=85.0,
        threshold_low=50.0,
        debounce_sec=1.5,
        update_interval_sec=0.5,
    )
    
    print("Configuration:")
    print(f"  Initial Temp: {ctrl.simulator.initial_temp}°F")
    print(f"  Warmup Duration: {ctrl.simulator.warmup_duration_sec}s")
    print(f"  Drift Rate: {ctrl.simulator.drift_rate}°F/s")
    print(f"  High Threshold: {ctrl.threshold_high}°F")
    print(f"  Low Threshold: {ctrl.threshold_low}°F")
    print(f"  Debounce: {ctrl.debounce_sec}s")
    print()
    
    # Run 10 second simulation (20 ticks at 0.5s interval)
    print("Running 10-second simulation...")
    print()
    
    results = []
    alerts = []
    
    for tick_num in range(20):
        result = ctrl.tick()
        results.append(result)
        
        # Print tick summary
        status_icon = "🔴" if result['state'] == "ALERT_HIGH" else (
            "🔵" if result['state'] == "ALERT_LOW" else "🟢"
        )
        
        print(
            f"{status_icon} [{result['simulation_time']:5.1f}s] "
            f"Temp: {result['temperature']:6.1f}°F | "
            f"State: {result['state']:12s} | "
            f"Tasks: {len(result['scheduled_tasks'])}"
        )
        
        # Log state changes
        if result['state_changed']:
            print(f"     ⚠️  ALERT: {result['alert_message']}")
            alerts.append({
                'time': result['simulation_time'],
                'state': result['state'],
                'message': result['alert_message'],
            })
        
        # Log persistence tasks
        for task in result['scheduled_tasks']:
            print(
                f"     📝 Persistence: {task['payload']['temperature']}°F @ {task['task_id']}"
            )
    
    print()
    print("=" * 80)
    print("SIMULATION SUMMARY")
    print("=" * 80)
    
    # Summary statistics
    temps = [r['temperature'] for r in results]
    print(f"Temperature Range: {min(temps):.1f}°F - {max(temps):.1f}°F")
    print(f"Total Ticks: {len(results)}")
    print(f"Simulation Time: {results[-1]['simulation_time']:.1f}s")
    print(f"State Changes: {len(alerts)}")
    
    if alerts:
        print("\nAlerts:")
        for alert in alerts:
            print(f"  • [{alert['time']:5.1f}s] {alert['state']}: {alert['message']}")
    
    persistence_count = sum(
        len(r['scheduled_tasks']) for r in results
    )
    print(f"\nPersistence Tasks: {persistence_count}")
    
    print()
    print("✅ Simulation completed successfully!")
    print()
    
    # Print sample response
    print("Sample Response (latest tick):")
    print(json.dumps(results[-1], indent=2))
    print()
    
    print("For more examples, see API_EXAMPLES.txt")
    print("For API specification, see API_CONTRACT.txt")


if __name__ == "__main__":
    main()
