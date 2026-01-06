"""
Unit Tests for Core Modules

Tests for TemperatureSimulator, YSMAI_Agent, and Scheduler classes.
"""

import unittest
import time
from simulator import TemperatureSimulator
from agent import YSMAI_Agent
from scheduler import Scheduler


class TestTemperatureSimulator(unittest.TestCase):
    """Unit tests for TemperatureSimulator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sim = TemperatureSimulator(
            initial_temp=60.0,
            warmup_duration_sec=5.0,
            drift_rate=0.5
        )
    
    def test_warmup_ramp(self):
        """Verify linear temperature rise during warmup phase."""
        # Run for 5 seconds of warmup (should go from 60 to ~70°F)
        temps = []
        for _ in range(10):
            temp = self.sim.tick(0.5)
            temps.append(temp)
        
        # First temp should be higher than initial
        self.assertGreater(temps[0], self.sim.initial_temp)
        
        # Temps should be monotonically increasing during warmup
        for i in range(1, 10):
            self.assertGreaterEqual(temps[i], temps[i-1] - 0.1)  # Allow small rounding
    
    def test_warmup_duration(self):
        """Verify warmup lasts correct duration."""
        # Tick for exactly warmup duration
        warmup_duration = 5.0
        ticks = int(warmup_duration / 0.5)
        
        for _ in range(ticks):
            self.sim.tick(0.5)
        
        # After warmup, should be ~70°F (initial 60 + 10°F ramp)
        self.assertGreater(self.sim.current_temp, 68.0)
        self.assertLess(self.sim.current_temp, 72.0)
    
    def test_drift_behavior(self):
        """Verify drift accumulates after warmup phase."""
        # Skip warmup
        for _ in range(10):
            self.sim.tick(0.5)
        
        temp_before_drift = self.sim.current_temp
        
        # Now in drift phase; run a few more ticks
        for _ in range(4):
            self.sim.tick(0.5)
        
        # Temperature should have changed due to drift
        temp_after_drift = self.sim.current_temp
        self.assertNotEqual(temp_before_drift, temp_after_drift)
    
    def test_fault_spike(self):
        """Verify fault injection applies magnitude correctly."""
        self.sim.set_fault_mode(enabled=True, magnitude=10.0)
        
        # Run several ticks with fault enabled
        temps = []
        for _ in range(5):
            temp = self.sim.tick(0.5)
            temps.append(temp)
        
        # With high fault magnitude, temps should vary significantly
        temp_range = max(temps) - min(temps)
        self.assertGreater(temp_range, 2.0)  # Should see noticeable variation
    
    def test_reset(self):
        """Verify state resets to initial values."""
        # Run some ticks
        for _ in range(10):
            self.sim.tick(0.5)
        
        # Reset
        self.sim.reset()
        
        # Check state
        self.assertEqual(self.sim.current_temp, self.sim.initial_temp)
        self.assertEqual(self.sim.elapsed_time, 0.0)
        self.assertFalse(self.sim.fault_injection_enabled)
    
    def test_temperature_bounds(self):
        """Verify temperature stays within realistic bounds."""
        self.sim.set_fault_mode(enabled=True, magnitude=50.0)  # Large fault
        
        for _ in range(100):
            temp = self.sim.tick(0.5)
            self.assertGreaterEqual(temp, 50.0)
            self.assertLessEqual(temp, 120.0)


class TestYSMAIAgent(unittest.TestCase):
    """Unit tests for YSMAI_Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = YSMAI_Agent(
            threshold_high=85.0,
            threshold_low=50.0,
            debounce_sec=1.5
        )
        self.current_time = time.time()
    
    def test_initial_state(self):
        """Verify agent starts in NORMAL state."""
        self.assertEqual(self.agent.get_state(), YSMAI_Agent.STATE_NORMAL)
    
    def test_debounce_high_threshold_single_spike(self):
        """Verify single spike doesn't trigger state change."""
        # One reading above threshold
        result = self.agent.update(90.0, self.current_time)
        
        # Should still be NORMAL (debounce not expired)
        self.assertEqual(result["state"], YSMAI_Agent.STATE_NORMAL)
        self.assertFalse(result["changed"])
    
    def test_debounce_high_threshold_expires(self):
        """Verify state change after debounce expires."""
        # First reading above threshold
        self.agent.update(90.0, self.current_time)
        
        # Second reading after debounce expires
        new_time = self.current_time + 2.0  # 2 seconds > 1.5 sec debounce
        result = self.agent.update(90.0, new_time)
        
        # Should transition to ALERT_HIGH
        self.assertEqual(result["state"], YSMAI_Agent.STATE_ALERT_HIGH)
        self.assertTrue(result["changed"])
        self.assertIsNotNone(result["alert_message"])
    
    def test_debounce_low_threshold_expires(self):
        """Verify low threshold triggers alert after debounce."""
        # Reading below low threshold
        self.agent.update(45.0, self.current_time)
        
        # After debounce expires
        new_time = self.current_time + 2.0
        result = self.agent.update(45.0, new_time)
        
        self.assertEqual(result["state"], YSMAI_Agent.STATE_ALERT_LOW)
        self.assertTrue(result["changed"])
    
    def test_state_recovery_after_debounce(self):
        """Verify state returns to NORMAL after condition clears."""
        # Transition to ALERT_HIGH
        self.agent.update(90.0, self.current_time)
        self.agent.update(90.0, self.current_time + 2.0)
        self.assertEqual(self.agent.get_state(), YSMAI_Agent.STATE_ALERT_HIGH)
        
        # Now temperature returns to normal
        self.agent.update(75.0, self.current_time + 2.5)
        
        # Recovery should also require debounce
        new_time = self.current_time + 4.1  # 1.6 sec after safe zone
        result = self.agent.update(75.0, new_time)
        
        self.assertEqual(result["state"], YSMAI_Agent.STATE_NORMAL)
        self.assertTrue(result["changed"])
    
    def test_alert_only_on_state_change(self):
        """Verify alert message only generated on state transitions."""
        # Transition to alert
        self.agent.update(90.0, self.current_time)
        result1 = self.agent.update(90.0, self.current_time + 2.0)
        self.assertIsNotNone(result1["alert_message"])
        
        # Subsequent tick in same state
        result2 = self.agent.update(90.0, self.current_time + 2.5)
        self.assertFalse(result2["changed"])
        self.assertIsNone(result2["alert_message"])
    
    def test_timestamp_tracking(self):
        """Verify timestamps are recorded correctly."""
        test_time = 1000.0
        self.agent.update(90.0, test_time)
        self.agent.update(90.0, test_time + 2.0)
        
        recorded_time = self.agent.get_timestamp()
        self.assertEqual(recorded_time, test_time + 2.0)


class TestScheduler(unittest.TestCase):
    """Unit tests for Scheduler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scheduler = Scheduler()
        self.current_time = 1000.0
    
    def test_task_ordering(self):
        """Verify min-heap returns tasks in chronological order."""
        # Add tasks out of order
        self.scheduler.add_task("task1", self.current_time + 5.0, {"data": "a"})
        self.scheduler.add_task("task2", self.current_time + 1.0, {"data": "b"})
        self.scheduler.add_task("task3", self.current_time + 3.0, {"data": "c"})
        
        # Pop all tasks
        tasks = self.scheduler.pop_due_tasks(self.current_time + 10.0)
        
        # Should be in order: task2, task3, task1
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0]["task_id"], "task2")
        self.assertEqual(tasks[1]["task_id"], "task3")
        self.assertEqual(tasks[2]["task_id"], "task1")
    
    def test_pop_due_tasks_filtering(self):
        """Verify pop_due_tasks only returns due tasks."""
        self.scheduler.add_task("task1", self.current_time + 2.0, {"data": "a"})
        self.scheduler.add_task("task2", self.current_time + 5.0, {"data": "b"})
        self.scheduler.add_task("task3", self.current_time + 8.0, {"data": "c"})
        
        # Pop at time 6
        tasks = self.scheduler.pop_due_tasks(self.current_time + 6.0)
        
        # Only task1 and task2 should be due
        self.assertEqual(len(tasks), 2)
        task_ids = [t["task_id"] for t in tasks]
        self.assertIn("task1", task_ids)
        self.assertIn("task2", task_ids)
        self.assertNotIn("task3", task_ids)
    
    def test_empty_queue(self):
        """Verify graceful handling of empty queue."""
        tasks = self.scheduler.pop_due_tasks(self.current_time)
        self.assertEqual(len(tasks), 0)
    
    def test_no_duplicate_pops(self):
        """Verify popped tasks are removed and not returned again."""
        self.scheduler.add_task("task1", self.current_time + 1.0, {"data": "a"})
        
        # Pop once
        tasks1 = self.scheduler.pop_due_tasks(self.current_time + 10.0)
        self.assertEqual(len(tasks1), 1)
        
        # Pop again
        tasks2 = self.scheduler.pop_due_tasks(self.current_time + 10.0)
        self.assertEqual(len(tasks2), 0)
    
    def test_clear(self):
        """Verify clear() removes all tasks."""
        self.scheduler.add_task("task1", self.current_time + 1.0, {"data": "a"})
        self.scheduler.add_task("task2", self.current_time + 2.0, {"data": "b"})
        
        self.scheduler.clear()
        
        self.assertEqual(self.scheduler.pending_count(), 0)
    
    def test_payload_preservation(self):
        """Verify task payloads are preserved."""
        payload = {"temp": 75.5, "state": "NORMAL", "timestamp": 1000.0}
        self.scheduler.add_task("log_task", self.current_time + 1.0, payload)
        
        tasks = self.scheduler.pop_due_tasks(self.current_time + 10.0)
        
        self.assertEqual(tasks[0]["payload"], payload)


if __name__ == "__main__":
    unittest.main()
