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
        
        # Generate synthetic sensor data for frontend
        # These would come from real sensors in production
        import math
        rpm = 500 + int(self.tick_count * 5) % 2500  # Simulated RPM
        oil_pressure_psi = 40.0 + (temperature - 60) * 0.3 + \
                          (rpm / 3000) * 15  # Pressure correlates with temp and RPM
        # Vibration RMS: V_RMS(t) = sqrt(BaseVib^2 + (FaultSeverity*RPMFactor)^2)
        base_vibration = 5.0
        temp_effect = abs((temperature - 72) * 0.5)
        rpm_effect = (rpm / 3000) * 8
        vibration_mms = math.sqrt(base_vibration**2 + temp_effect**2 + rpm_effect**2)
        voltage_v = 13.2 + (rpm / 3000) * 0.5 - (temperature - 72) * 0.01
        
        # Clamp values to valid ranges
        rpm = max(0, min(3000, rpm))
        oil_pressure_psi = max(0.0, min(80.0, oil_pressure_psi))
        vibration_mms = max(0.0, min(50.0, vibration_mms))
        voltage_v = max(10.0, min(15.0, voltage_v))
        
        # Get ML insights if available
        ml_insights = self._get_ml_insights(
            temperature, rpm, oil_pressure_psi, vibration_mms
        )
        
        # Build response
        response = {
            "timestamp": self.current_time,
            "temperature": round(temperature, 1),
            "rpm": rpm,
            "oil_pressure_psi": round(oil_pressure_psi, 1),
            "vibration_mms": round(vibration_mms, 1),
            "voltage_v": round(voltage_v, 1),
            "state": agent_result["state"],
            "state_changed": agent_result["changed"],
            "alert_message": agent_result["alert_message"],
            "scheduled_tasks": scheduled_tasks,
            "simulation_time": self.simulation_time,
            "tick_count": self.tick_count,
            "ml_insights": ml_insights,
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
    
    def _get_ml_insights(
        self,
        temperature: float,
        rpm: int,
        oil_pressure_psi: float,
        vibration_mms: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Get ML predictions for current sensor data.
        
        Args:
            temperature: Current temperature (°F)
            rpm: Current RPM
            oil_pressure_psi: Current oil pressure
            vibration_mms: Current vibration level
            
        Returns:
            Dictionary with ML predictions or None if ML unavailable
        """
        try:
            import time as time_module
            from ml_training_kaggle import MLModelTrainer
            
            # Lazy load and cache trainer
            if not hasattr(self, '_ml_trainer'):
                self._ml_trainer = MLModelTrainer()
                self._ml_trainer.load_all_models()
            
            trainer = self._ml_trainer
            
            # Get predictions with timing
            start_time = time_module.time()
            fault_pred = trainer.predict_fault(
                rpm=rpm,
                pressure=oil_pressure_psi,
                temp=temperature,
                vib=vibration_mms
            )
            fault_inference_time = (time_module.time() - start_time) * 1000  # Convert to ms
            
            start_time = time_module.time()
            vibration_pred = trainer.detect_vibration_anomaly(
                bearing_1=vibration_mms,
                bearing_2=vibration_mms * 0.9
            )
            vibration_inference_time = (time_module.time() - start_time) * 1000  # Convert to ms
            
            start_time = time_module.time()
            pressure_pred = trainer.predict_pressure(flow_rate=rpm/100)
            pressure_inference_time = (time_module.time() - start_time) * 1000  # Convert to ms
            
            return {
                "fault_detection": {
                    "detected": fault_pred.get('fault', False),
                    "confidence": fault_pred.get('confidence', 0.0),
                    "inference_time": fault_inference_time
                },
                "vibration_anomaly": {
                    "detected": vibration_pred.get('anomaly', False),
                    "score": vibration_pred.get('score', 0.0),
                    "inference_time": vibration_inference_time
                },
                "pressure_prediction": {
                    "predicted_pressure": pressure_pred.get('predicted_pressure', oil_pressure_psi),
                    "actual_pressure": oil_pressure_psi,
                    "confidence": pressure_pred.get('confidence', 0.85),
                    "inference_time": pressure_inference_time
                }
            }
        
        except Exception as e:
            # Graceful fallback if ML unavailable
            return None
    
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
