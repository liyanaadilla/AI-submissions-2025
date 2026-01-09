#!/usr/bin/env python3
"""
YSMAI Backend Final Validation Test Suite

Comprehensive test of all backend functionality required by the frontend:
1. API contract validation (response schema)
2. Data type verification
3. State machine transitions
4. ML predictions accuracy
5. Error handling and recovery
6. Performance benchmarks
7. Extended simulation runs

This test ensures the backend is production-ready for frontend integration.
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controller import SimulationController
from agent_enhanced import EnhancedYSMAI_Agent
from ml_training_kaggle import MLModelTrainer


class BackendValidator:
    """Comprehensive backend validation suite."""
    
    def __init__(self):
        self.test_results = []
        self.controller = None
        self.start_time = time.time()
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
    
    def log_test(self, name: str, passed: bool, message: str = ""):
        """Log a test result."""
        self.test_count += 1
        if passed:
            self.pass_count += 1
            status = "✓ PASS"
        else:
            self.fail_count += 1
            status = "✗ FAIL"
        
        result = {
            'test': name,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"  {status}: {name}" + (f" - {message}" if message else ""))
    
    def print_header(self, title: str):
        """Print section header."""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    
    # ========== TEST 1: API CONTRACT VALIDATION ==========
    
    def test_api_contract(self):
        """Test 1: Verify API response matches contract."""
        self.print_header("TEST 1: API CONTRACT VALIDATION")
        
        self.controller = SimulationController()
        response = self.controller.tick()
        
        # Required top-level fields
        required_fields = [
            'timestamp', 'temperature', 'rpm', 'oil_pressure_psi',
            'vibration_mms', 'voltage_v', 'state', 'state_changed',
            'alert_message', 'simulation_time', 'scheduled_tasks',
            'ml_insights'
        ]
        
        for field in required_fields:
            present = field in response
            self.log_test(
                f"Field '{field}' present",
                present,
                f"Value: {response.get(field, 'MISSING')}"
            )
        
        # Verify state is valid
        valid_states = ['NORMAL', 'ALERT_HIGH', 'ALERT_LOW']
        state_valid = response['state'] in valid_states
        self.log_test(
            f"State valid",
            state_valid,
            f"State: {response['state']}"
        )
        
        # Verify state_changed is boolean
        self.log_test(
            "state_changed is boolean",
            isinstance(response['state_changed'], bool)
        )
        
        # Verify alert_message is string or None
        alert_valid = isinstance(response['alert_message'], (str, type(None)))
        self.log_test(
            "alert_message is string or None",
            alert_valid,
            f"Type: {type(response['alert_message'])}"
        )
    
    # ========== TEST 2: DATA TYPE VALIDATION ==========
    
    def test_data_types(self):
        """Test 2: Verify all data types match schema."""
        self.print_header("TEST 2: DATA TYPE VALIDATION")
        
        response = self.controller.tick()
        
        # Expected types
        type_schema = {
            'timestamp': (int, float),
            'temperature': (int, float),
            'rpm': (int, float),
            'oil_pressure_psi': (int, float),
            'vibration_mms': (int, float),
            'voltage_v': (int, float),
            'state': str,
            'state_changed': bool,
            'alert_message': (str, type(None)),
            'simulation_time': (int, float),
            'scheduled_tasks': list,
        }
        
        for field, expected_type in type_schema.items():
            value = response.get(field)
            if isinstance(expected_type, tuple):
                type_valid = isinstance(value, expected_type)
            else:
                type_valid = isinstance(value, expected_type)
            
            self.log_test(
                f"Type of '{field}' correct",
                type_valid,
                f"Expected: {expected_type}, Got: {type(value)}"
            )
    
    # ========== TEST 3: SENSOR DATA RANGES ==========
    
    def test_sensor_ranges(self):
        """Test 3: Verify sensor values are within expected ranges."""
        self.print_header("TEST 3: SENSOR DATA RANGES")
        
        # Collect data over 10 ticks to verify consistency
        responses = []
        for _ in range(10):
            responses.append(self.controller.tick())
        
        # Define ranges (from data_schema)
        ranges = {
            'temperature': (25.0, 115.0),  # °F
            'rpm': (0, 3000),
            'oil_pressure_psi': (0.0, 80.0),
            'vibration_mms': (0.0, 50.0),
            'voltage_v': (10.0, 15.0)
        }
        
        for field, (min_val, max_val) in ranges.items():
            values = [r[field] for r in responses]
            all_in_range = all(min_val <= v <= max_val for v in values)
            
            self.log_test(
                f"'{field}' always in range [{min_val}, {max_val}]",
                all_in_range,
                f"Min: {min(values):.2f}, Max: {max(values):.2f}"
            )
    
    # ========== TEST 4: STATE TRANSITIONS ==========
    
    def test_state_transitions(self):
        """Test 4: Verify state machine transitions work correctly."""
        self.print_header("TEST 4: STATE TRANSITIONS")
        
        # Reset controller
        self.controller.reset_simulation()
        
        # Test 1: Normal → Alert High
        print("\n  Scenario: Temperature rise to trigger ALERT_HIGH")
        self.controller.set_fault_injection(True, magnitude=20)
        
        transition_found = False
        state_sequence = []
        
        for i in range(50):
            response = self.controller.tick()
            state_sequence.append(response['state'])
            
            if i > 0 and response['state_changed']:
                if response['state'] == 'ALERT_HIGH':
                    transition_found = True
                    print(f"    Found transition at tick {i}: {state_sequence[i-1]} → {state_sequence[i]}")
                    break
        
        self.log_test(
            "NORMAL → ALERT_HIGH transition occurs",
            transition_found,
            f"After {i} ticks"
        )
        
        # Test 2: Alert → Normal (recovery)
        print("\n  Scenario: Temperature drop to trigger recovery")
        self.controller.set_fault_injection(False)
        
        recovery_found = False
        recovery_ticks = 0
        
        for i in range(100):
            response = self.controller.tick()
            recovery_ticks += 1
            
            if response['state'] == 'NORMAL':
                recovery_found = True
                print(f"    Found recovery at tick {recovery_ticks}: → NORMAL")
                break
        
        self.log_test(
            "ALERT_HIGH → NORMAL recovery occurs",
            recovery_found,
            f"After {recovery_ticks} ticks"
        )
    
    # ========== TEST 5: ML INTEGRATION ==========
    
    def test_ml_integration(self):
        """Test 5: Verify ML predictions are included and accurate."""
        self.print_header("TEST 5: ML INTEGRATION")
        
        # Check if ML models are trained
        trainer = MLModelTrainer()
        models_loaded = trainer.load_all_models()
        
        self.log_test(
            "ML models can be loaded",
            models_loaded,
            "3 models loaded: fault_detector, vibration_detector, pressure_predictor"
        )
        
        # Verify ML insights in response
        response = self.controller.tick()
        has_ml = 'ml_insights' in response and response['ml_insights'] is not None
        
        self.log_test(
            "Response includes ml_insights",
            has_ml
        )
        
        if has_ml:
            ml = response['ml_insights']
            
            # Check fault detection
            has_fault = 'fault_detection' in ml
            self.log_test(
                "ml_insights includes fault_detection",
                has_fault
            )
            
            # Check vibration anomaly
            has_vibration = 'vibration_anomaly' in ml
            self.log_test(
                "ml_insights includes vibration_anomaly",
                has_vibration
            )
            
            # Check pressure prediction
            has_pressure = 'pressure_prediction' in ml
            self.log_test(
                "ml_insights includes pressure_prediction",
                has_pressure
            )
            
            # Verify prediction structure
            if has_pressure:
                pred = ml['pressure_prediction']
                has_predicted = 'predicted_pressure' in pred
                self.log_test(
                    "Pressure prediction includes predicted_pressure",
                    has_predicted,
                    f"Value: {pred.get('predicted_pressure', 'MISSING'):.2f} PSI"
                )
    
    # ========== TEST 6: ALERT MANAGEMENT ==========
    
    def test_alert_management(self):
        """Test 6: Verify alerts are properly managed."""
        self.print_header("TEST 6: ALERT MANAGEMENT")
        
        self.controller.reset_simulation()
        
        # Trigger an alert by injecting fault
        self.controller.set_fault_injection(True, magnitude=15)
        
        alert_triggered = False
        alert_count = 0
        
        for i in range(100):
            response = self.controller.tick()
            
            if response['alert_message'] is not None:
                alert_count += 1
                if not alert_triggered:
                    alert_triggered = True
                    print(f"  Alert triggered at tick {i}:")
                    print(f"  Message: {response['alert_message']}")
                    print(f"  State: {response['state']}")
        
        self.log_test(
            "Alerts are triggered on temperature spike",
            alert_triggered,
            f"Alert occurred {alert_count} times during 100 ticks"
        )
    
    # ========== TEST 7: PERSISTENCE (SCHEDULED TASKS) ==========
    
    def test_scheduled_tasks(self):
        """Test 7: Verify scheduled persistence tasks."""
        self.print_header("TEST 7: SCHEDULED TASKS")
        
        self.controller.reset_simulation()
        
        has_tasks = False
        task_count = 0
        
        for i in range(100):
            response = self.controller.tick()
            
            if response['scheduled_tasks'] and len(response['scheduled_tasks']) > 0:
                if not has_tasks:
                    has_tasks = True
                    task_count = len(response['scheduled_tasks'])
                    print(f"  Tasks found at tick {i}:")
                    for task in response['scheduled_tasks']:
                        print(f"    - {task.get('task_id', 'UNKNOWN')}")
        
        self.log_test(
            "Scheduled tasks are generated",
            has_tasks,
            f"Found {task_count} task(s)"
        )
    
    # ========== TEST 8: PERFORMANCE BENCHMARKS ==========
    
    def test_performance(self):
        """Test 8: Verify performance meets targets."""
        self.print_header("TEST 8: PERFORMANCE BENCHMARKS")
        
        self.controller.reset_simulation()
        
        # Warm up
        for _ in range(10):
            self.controller.tick()
        
        # Measure 100 ticks
        tick_times = []
        
        for _ in range(100):
            start = time.time()
            self.controller.tick()
            elapsed = (time.time() - start) * 1000  # Convert to ms
            tick_times.append(elapsed)
        
        avg_time = sum(tick_times) / len(tick_times)
        max_time = max(tick_times)
        min_time = min(tick_times)
        p95_time = sorted(tick_times)[int(len(tick_times) * 0.95)]
        
        # Targets
        self.log_test(
            "Average tick time < 100ms",
            avg_time < 100,
            f"Actual: {avg_time:.2f}ms"
        )
        
        self.log_test(
            "Max tick time < 500ms",
            max_time < 500,
            f"Actual: {max_time:.2f}ms"
        )
        
        self.log_test(
            "P95 tick time < 200ms",
            p95_time < 200,
            f"Actual: {p95_time:.2f}ms"
        )
        
        print(f"\n  Performance Summary:")
        print(f"    Average: {avg_time:.2f}ms")
        print(f"    Min: {min_time:.2f}ms")
        print(f"    Max: {max_time:.2f}ms")
        print(f"    P95: {p95_time:.2f}ms")
    
    # ========== TEST 9: EXTENDED SIMULATION RUN ==========
    
    def test_extended_run(self):
        """Test 9: Verify stability over 5-minute run."""
        self.print_header("TEST 9: EXTENDED SIMULATION RUN (5 minutes)")
        
        self.controller.reset_simulation()
        
        tick_count = 0
        errors = 0
        states_seen = set()
        
        start_time = time.time()
        target_duration = 300  # 5 minutes
        
        print(f"  Running for {target_duration} seconds...")
        
        while time.time() - start_time < target_duration:
            try:
                response = self.controller.tick()
                tick_count += 1
                states_seen.add(response['state'])
            except Exception as e:
                errors += 1
                print(f"  Error at tick {tick_count}: {e}")
        
        elapsed = time.time() - start_time
        expected_ticks = int(elapsed)  # ~1 tick per second
        
        self.log_test(
            "Extended run completes without crashes",
            errors == 0,
            f"Completed {tick_count} ticks in {elapsed:.1f}s"
        )
        
        self.log_test(
            "Tick count reasonable",
            tick_count > expected_ticks * 0.9,  # Allow 10% variance
            f"Expected ~{expected_ticks}, got {tick_count}"
        )
        
        self.log_test(
            "Multiple states observed",
            len(states_seen) > 1,
            f"States: {', '.join(sorted(states_seen))}"
        )
        
        print(f"\n  Extended Run Summary:")
        print(f"    Duration: {elapsed:.1f}s")
        print(f"    Ticks: {tick_count}")
        print(f"    States: {', '.join(sorted(states_seen))}")
        print(f"    Errors: {errors}")
    
    # ========== TEST 10: RESET FUNCTIONALITY ==========
    
    def test_reset(self):
        """Test 10: Verify reset functionality."""
        self.print_header("TEST 10: RESET FUNCTIONALITY")
        
        # Get initial state
        self.controller.reset_simulation()
        initial_response = self.controller.tick()
        
        # Run for a while
        for _ in range(50):
            self.controller.tick()
        
        # Reset
        self.controller.reset_simulation()
        reset_response = self.controller.tick()
        
        # Check state is back to initial
        self.log_test(
            "Reset returns to NORMAL state",
            reset_response['state'] == 'NORMAL',
            f"State: {reset_response['state']}"
        )
        
        self.log_test(
            "Reset clears alert_message",
            reset_response['alert_message'] is None,
            f"Message: {reset_response['alert_message']}"
        )
        
        self.log_test(
            "Reset returns simulation_time to ~0",
            reset_response['simulation_time'] < 5,
            f"Time: {reset_response['simulation_time']:.2f}s"
        )
    
    # ========== TEST 11: FAULT INJECTION ==========
    
    def test_fault_injection(self):
        """Test 11: Verify fault injection mechanism."""
        self.print_header("TEST 11: FAULT INJECTION")
        
        self.controller.reset_simulation()
        
        # Enable fault injection
        self.controller.set_fault_injection(True, magnitude=25)
        
        # Collect temperatures
        temps = []
        for _ in range(100):
            response = self.controller.tick()
            temps.append(response['temperature'])
        
        # Check for spikes (variation should increase with faults)
        variation = max(temps) - min(temps)
        
        self.log_test(
            "Fault injection causes temperature variation",
            variation > 10,  # At least 10°F variation
            f"Variation: {variation:.2f}°F"
        )
        
        # Disable fault injection
        self.controller.set_fault_injection(False)
        
        # Temperatures should stabilize
        temps_stable = []
        for _ in range(50):
            response = self.controller.tick()
            temps_stable.append(response['temperature'])
        
        variation_stable = max(temps_stable) - min(temps_stable)
        
        self.log_test(
            "Fault injection disables correctly",
            variation_stable < variation,
            f"Variation after disable: {variation_stable:.2f}°F"
        )
    
    # ========== GENERATE REPORT ==========
    
    def generate_report(self):
        """Generate comprehensive test report."""
        self.print_header("FINAL TEST REPORT")
        
        elapsed = time.time() - self.start_time
        
        print(f"Test Summary:")
        print(f"  Total Tests: {self.test_count}")
        print(f"  Passed: {self.pass_count} ✓")
        print(f"  Failed: {self.fail_count} ✗")
        print(f"  Pass Rate: {(self.pass_count/self.test_count*100):.1f}%")
        print(f"  Duration: {elapsed:.1f}s")
        
        # Export results
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': self.test_count,
                'passed': self.pass_count,
                'failed': self.fail_count,
                'pass_rate': (self.pass_count/self.test_count*100),
                'duration_seconds': elapsed
            },
            'results': self.test_results
        }
        
        report_path = "backend_validation_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n  Report saved to: {report_path}")
        
        # Determine overall status
        if self.fail_count == 0:
            print(f"\n  ✅ BACKEND READY FOR PRODUCTION")
            return 0
        else:
            print(f"\n  ⚠️  BACKEND HAS {self.fail_count} FAILING TEST(S)")
            return 1


def main():
    """Run complete backend validation."""
    print("\n" + "="*70)
    print("  YSMAI BACKEND - FINAL VALIDATION TEST SUITE")
    print("  Comprehensive Pre-Frontend Integration Testing")
    print("="*70)
    
    validator = BackendValidator()
    
    try:
        # Run all tests
        validator.test_api_contract()
        validator.test_data_types()
        validator.test_sensor_ranges()
        validator.test_state_transitions()
        validator.test_ml_integration()
        validator.test_alert_management()
        validator.test_scheduled_tasks()
        validator.test_performance()
        validator.test_extended_run()
        validator.test_reset()
        validator.test_fault_injection()
        
        # Generate report
        return_code = validator.generate_report()
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return return_code


if __name__ == "__main__":
    sys.exit(main())
