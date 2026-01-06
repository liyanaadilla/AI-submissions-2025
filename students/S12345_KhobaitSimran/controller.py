"""
SimulationController Module

Main orchestration class that coordinates Simulator, Agent, and Scheduler.
Provides the core API tick() method for frontend consumption.
"""

import json
import time
from typing import Dict, Any, Optional
from simulator import TemperatureSimulator
from agent import YSMAI_Agent
from scheduler import Scheduler


class SimulationController:
    """
    Main simulation controller integrating all components.
    
    Manages:
    - Temperature simulation
    - Agent state tracking
    - Task scheduling
    - Persistence task auto-scheduling
    - JSON serialization of outputs
    """
    
    def __init__(
        self,
        initial_temp: float = 60.0,
        warmup_duration: float = 5.0,
        drift_rate: float = 0.5,
        threshold_high: float = 85.0,
        threshold_low: float = 50.0,
        debounce_sec: float = 1.5,
        update_interval_sec: float = 0.5,
    ):
        """
        Initialize the SimulationController.
        
        Args:
            initial_temp: Starting temperature in °F (default: 60)
            warmup_duration: Warmup phase duration in seconds (default: 5)
            drift_rate: Drift rate in °F/second (default: 0.5)
            threshold_high: High temperature threshold in °F (default: 85)
            threshold_low: Low temperature threshold in °F (default: 50)
            debounce_sec: Debounce duration in seconds (default: 1.5)
            update_interval_sec: Time between ticks in seconds (default: 0.5)
        """
        # Components
        self.simulator = TemperatureSimulator(
            initial_temp=initial_temp,
            warmup_duration_sec=warmup_duration,
            drift_rate=drift_rate,
        )
        self.agent = YSMAI_Agent(
            threshold_high=threshold_high,
            threshold_low=threshold_low,
            debounce_sec=debounce_sec,
        )
        self.scheduler = Scheduler()
        
        # Parameters
        self.update_interval_sec = update_interval_sec
        self.threshold_high = threshold_high
        self.threshold_low = threshold_low
        self.debounce_sec = debounce_sec
        
        # State tracking
        self.current_time = time.time()
        self.simulation_start_time = self.current_time
        self.simulation_time = 0.0
        self.tick_count = 0
        
        # Persistence task tracking
        self.persistence_interval = 5.0  # Schedule persistence task every 5 seconds
        self.last_persistence_time = self.current_time
        self.persistence_task_count = 0
        
        # Fault injection
        self.fault_injection_enabled = False
        self.fault_magnitude = 0.0
    
    def tick(self) -> Dict[str, Any]:
        """
        Execute one simulation tick and return results.
        
        Returns:
            Dictionary with simulation state, temperature, agent state, and tasks
        """
        self.tick_count += 1
        
        # Update simulation time
        self.simulation_time += self.update_interval_sec
        self.current_time = self.simulation_start_time + self.simulation_time
        
        # Simulator tick
        temperature = self.simulator.tick(self.update_interval_sec)
        
        # Agent update
        agent_result = self.agent.update(temperature, self.current_time)
        
        # Check for due scheduler tasks
        due_tasks = self.scheduler.pop_due_tasks(self.current_time)
        scheduled_tasks = [
            {
                "task_id": task["task_id"],
                "payload": task["payload"],
                "due_time": task["due_time"],
            }
            for task in due_tasks
        ]
        
        # Auto-schedule persistence tasks every 5 seconds
        self._schedule_persistence_tasks(temperature, agent_result["state"])
        
        # Build response
        response = {
            "timestamp": self.current_time,
            "temperature": round(temperature, 1),
            "state": agent_result["state"],
            "state_changed": agent_result["changed"],
            "alert_message": agent_result["alert_message"],
            "scheduled_tasks": scheduled_tasks,
            "simulation_time": self.simulation_time,
            "tick_count": self.tick_count,
        }
        
        # Optional: include debug info
        if False:  # Set to True to enable debug output
            response["debug_info"] = {
                "simulator_state": self.simulator.get_state(),
                "agent_state": self.agent.get_debug_state(),
                "scheduler_state": self.scheduler.get_debug_state(),
            }
        
        return response
    
    def _schedule_persistence_tasks(self, temperature: float, state: str) -> None:
        """
        Auto-schedule persistence tasks every 5 seconds.
        
        Args:
            temperature: Current temperature
            state: Current agent state
        """
        time_since_last_persistence = self.current_time - self.last_persistence_time
        
        if time_since_last_persistence >= self.persistence_interval:
            # Schedule persistence task
            task_id = f"persist_{self.persistence_task_count}"
            payload = {
                "type": "persistence",
                "timestamp": self.current_time,
                "temperature": round(temperature, 1),
                "state": state,
            }
            
            self.scheduler.add_task(
                task_id=task_id,
                due_time_unix=self.current_time,
                payload=payload,
            )
            
            self.persistence_task_count += 1
            self.last_persistence_time = self.current_time
    
    def set_fault_injection(self, enabled: bool, magnitude: float = 0.0) -> None:
        """
        Enable or disable fault injection mode.
        
        Args:
            enabled: Whether fault injection is active
            magnitude: Max magnitude of temperature spikes/dips in °F
        """
        self.fault_injection_enabled = enabled
        self.fault_magnitude = magnitude
        self.simulator.set_fault_mode(enabled, magnitude)
    
    def reset_simulation(self) -> None:
        """Reset the simulation to initial state."""
        self.simulator.reset()
        self.agent = YSMAI_Agent(
            threshold_high=self.threshold_high,
            threshold_low=self.threshold_low,
            debounce_sec=self.debounce_sec,
        )
        self.scheduler.clear()
        
        self.current_time = time.time()
        self.simulation_start_time = self.current_time
        self.simulation_time = 0.0
        self.tick_count = 0
        self.last_persistence_time = self.current_time
        self.persistence_task_count = 0
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get full controller state (for debugging).
        
        Returns:
            Dictionary with all state variables
        """
        return {
            "tick_count": self.tick_count,
            "simulation_time": self.simulation_time,
            "current_time": self.current_time,
            "simulator_state": self.simulator.get_state(),
            "agent_state": self.agent.get_debug_state(),
            "scheduler_state": self.scheduler.get_debug_state(),
            "fault_injection_enabled": self.fault_injection_enabled,
            "fault_magnitude": self.fault_magnitude,
        }
    
    @staticmethod
    def to_json(response: Dict[str, Any]) -> str:
        """
        Convert response dict to JSON string.
        
        Args:
            response: Response dictionary from tick()
        
        Returns:
            JSON string
        """
        return json.dumps(response, indent=2)
