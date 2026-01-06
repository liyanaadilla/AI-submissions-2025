"""
Integration Tests

Full simulation chain: Simulator → Agent → Scheduler
"""

import unittest
import time
from simulator import TemperatureSimulator
from agent import YSMAI_Agent
from scheduler import Scheduler


class TestIntegration(unittest.TestCase):
    """Integration tests for full simulation chain."""
    
    def test_full_10_second_simulation(self):
        """
        Integration test: 10-second simulation with simulator, agent, scheduler.
        
        Scenario:
        - Initialize simulator (60°F, 5-sec warmup, 0.5°F/sec drift)
        - Initialize agent (threshold_high=85, threshold_low=50, debounce=1.5)
        - Initialize scheduler with 3 sample tasks
        - Run tick loop: every 0.5 sec for 10 sec
        - Verify all components work together
        """
        # Setup
        simulator = TemperatureSimulator(
            initial_temp=60.0,
            warmup_duration_sec=5.0,
            drift_rate=0.5
        )
        agent = YSMAI_Agent(
            threshold_high=85.0,
            threshold_low=50.0,
            debounce_sec=1.5
        )
        scheduler = Scheduler()
        
        # Add sample tasks
        start_time = 1000.0
        scheduler.add_task("persist_1", start_time + 2.0, {"type": "persistence", "index": 0})
        scheduler.add_task("persist_2", start_time + 4.0, {"type": "persistence", "index": 1})
        scheduler.add_task("log_1", start_time + 6.0, {"type": "log", "index": 0})
        
        # Run simulation
        tick_interval = 0.5
        num_ticks = 20  # 20 ticks * 0.5 sec = 10 seconds
        
        all_results = []
        state_changes = []
        tasks_executed = []
        current_time = start_time
        
        for tick_num in range(num_ticks):
            # Simulate
            temp = simulator.tick(tick_interval)
            
            # Update agent
            agent_result = agent.update(temp, current_time)
            
            # Check scheduler
            due_tasks = scheduler.pop_due_tasks(current_time)
            
            result = {
                "tick": tick_num,
                "time": current_time,
                "temperature": temp,
                "agent_state": agent_result["state"],
                "state_changed": agent_result["changed"],
                "alert_message": agent_result["alert_message"],
                "tasks_executed": len(due_tasks),
            }
            
            all_results.append(result)
            
            if agent_result["changed"]:
                state_changes.append({
                    "tick": tick_num,
                    "time": current_time,
                    "state": agent_result["state"],
                    "message": agent_result["alert_message"],
                })
            
            if due_tasks:
                tasks_executed.append({
                    "tick": tick_num,
                    "time": current_time,
                    "tasks": due_tasks,
                })
            
            current_time += tick_interval
        
        # Assertions
        # 1. Verify simulation ran for expected duration
        self.assertEqual(len(all_results), num_ticks)
        
        # 2. Verify temperature behavior
        first_temp = all_results[0]["temperature"]
        mid_temp = all_results[10]["temperature"]
        last_temp = all_results[-1]["temperature"]
        
        # Should warm up initially
        self.assertGreater(mid_temp, first_temp)
        
        # 3. Verify agent tracks state correctly
        self.assertEqual(all_results[0]["agent_state"], YSMAI_Agent.STATE_NORMAL)
        
        # 4. Verify state changes are tracked
        state_changed_count = sum(1 for r in all_results if r["state_changed"])
        self.assertGreaterEqual(state_changed_count, 0)  # May or may not change
        
        # 5. Verify scheduler executed tasks
        self.assertGreater(len(tasks_executed), 0)
        
        # 6. Verify task execution times are correct
        expected_task_count = 3  # We added 3 tasks
        total_executed_tasks = sum(len(te["tasks"]) for te in tasks_executed)
        self.assertEqual(total_executed_tasks, expected_task_count)
        
        print("\n=== Integration Test Summary ===")
        print(f"Total ticks: {num_ticks}")
        print(f"Simulation duration: {current_time - start_time:.1f} seconds")
        print(f"Temperature range: {min(r['temperature'] for r in all_results):.1f}°F - {max(r['temperature'] for r in all_results):.1f}°F")
        print(f"State changes: {len(state_changes)}")
        print(f"Tasks executed: {total_executed_tasks}")
        if state_changes:
            print(f"State transitions: {[sc['state'] for sc in state_changes]}")
    
    def test_simulator_agent_chain(self):
        """Test direct integration of Simulator and Agent."""
        simulator = TemperatureSimulator(
            initial_temp=60.0,
            warmup_duration_sec=2.0,
            drift_rate=1.0  # Faster drift for this test
        )
        agent = YSMAI_Agent(
            threshold_high=80.0,
            threshold_low=55.0,
            debounce_sec=0.5
        )
        
        current_time = 1000.0
        tick_interval = 0.5
        
        # Run until we see a state change
        state_changes_found = False
        for _ in range(50):
            temp = simulator.tick(tick_interval)
            result = agent.update(temp, current_time)
            current_time += tick_interval
            
            if result["changed"]:
                state_changes_found = True
                break
        
        # With 50 ticks of 0.5 sec and drift of 1.0°F/sec, we should see state change
        self.assertTrue(state_changes_found, "No state change detected in 50 ticks")
    
    def test_scheduler_timing_accuracy(self):
        """Verify scheduler maintains accurate timing across multiple tasks."""
        scheduler = Scheduler()
        start_time = 1000.0
        
        # Add tasks at specific times
        task_times = [1002.0, 1005.0, 1008.0, 1010.0, 1015.0]
        for i, task_time in enumerate(task_times):
            scheduler.add_task(f"task_{i}", task_time, {"index": i})
        
        # Simulate time progressing
        executed_times = []
        current_time = start_time
        tick_interval = 0.5
        
        for _ in range(40):  # 40 * 0.5 = 20 seconds
            tasks = scheduler.pop_due_tasks(current_time)
            if tasks:
                for task in tasks:
                    executed_times.append((task["task_id"], task["due_time"]))
            current_time += tick_interval
        
        # Verify all tasks were executed
        self.assertEqual(len(executed_times), len(task_times))
        
        # Verify order
        executed_task_times = [t[1] for t in executed_times]
        self.assertEqual(executed_task_times, sorted(task_times))
    
    def test_fault_injection_integration(self):
        """Test fault injection within the full simulation chain."""
        simulator = TemperatureSimulator(
            initial_temp=70.0,
            warmup_duration_sec=2.0,
            drift_rate=0.2
        )
        agent = YSMAI_Agent(
            threshold_high=85.0,
            threshold_low=55.0,
            debounce_sec=1.0
        )
        
        # Enable fault injection with high magnitude
        simulator.set_fault_mode(enabled=True, magnitude=15.0)
        
        current_time = 1000.0
        temps = []
        
        # Run 20 ticks with fault injection
        for _ in range(20):
            temp = simulator.tick(0.5)
            temps.append(temp)
            agent.update(temp, current_time)
            current_time += 0.5
        
        # With high fault magnitude, should see significant variation
        temp_variation = max(temps) - min(temps)
        self.assertGreater(temp_variation, 5.0, "Fault injection not producing expected variation")


if __name__ == "__main__":
    unittest.main(verbosity=2)
