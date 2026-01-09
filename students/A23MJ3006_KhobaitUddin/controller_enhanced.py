"""
Enhanced SimulationController Module

Main orchestration class with:
- 6-state FSM via YSMAI_EnhancedAgent
- Dynamic priority scheduling via DynamicScheduler
- Yanmar DTC codes
- Drift rate and RUL estimation
- Full ML integration
- Decision tracking and report generation
"""

import json
import time
import math
from typing import Dict, Any, Optional
from simulator import TemperatureSimulator
from agent_enhanced import YSMAI_EnhancedAgent
from scheduler_dynamic import DynamicScheduler
from decision_tracker import get_decision_tracker, DecisionTracker


class EnhancedSimulationController:
    """
    Enhanced simulation controller with 6-state FSM and dynamic scheduling.
    
    Manages:
    - Multi-sensor simulation (temp, pressure, vibration, voltage)
    - Enhanced agent with DTCs and RUL
    - Dynamic maintenance scheduling
    - ML predictions
    - Firebase-ready output format
    """
    
    def __init__(
        self,
        initial_temp: float = 60.0,
        warmup_duration: float = 5.0,
        drift_rate: float = 0.5,
        update_interval_sec: float = 0.5,
        # Thresholds passed to agent
        temp_warning: float = 221.0,
        temp_critical: float = 226.0,
    ):
        """Initialize the enhanced controller."""
        # Components
        self.simulator = TemperatureSimulator(
            initial_temp=initial_temp,
            warmup_duration_sec=warmup_duration,
            drift_rate=drift_rate,
        )
        
        self.agent = YSMAI_EnhancedAgent(
            temp_warning=temp_warning,
            temp_critical=temp_critical,
        )
        
        self.scheduler = DynamicScheduler()
        
        # Decision tracker
        self.decision_tracker = get_decision_tracker()
        
        # Parameters
        self.update_interval_sec = update_interval_sec
        
        # State tracking
        self.current_time = time.time()
        self.simulation_start_time = self.current_time
        self.simulation_time = 0.0
        self.tick_count = 0
        
        # Hours tracking for scheduler
        self.simulation_hours = 0.0
        
        # Fault injection
        self.fault_injection_enabled = False
        self.fault_magnitude = 0.0
        
        # ML trainer (lazy loaded)
        self._ml_trainer = None
        self._ml_load_attempted = False
    
    def tick(self) -> Dict[str, Any]:
        """
        Execute one simulation tick and return comprehensive results.
        
        Returns:
            Dictionary with all simulation data for frontend and Firebase
        """
        self.tick_count += 1
        
        # Update simulation time
        self.simulation_time += self.update_interval_sec
        self.current_time = self.simulation_start_time + self.simulation_time
        
        # Convert to hours for scheduler
        elapsed_hours = self.update_interval_sec / 3600.0
        self.simulation_hours += elapsed_hours
        
        # Simulator tick - get temperature
        temperature = self.simulator.tick(self.update_interval_sec)
        
        # Generate correlated sensor data
        sensors = self._generate_sensor_data(temperature)
        
        # Agent update with all sensors
        agent_result = self.agent.update(
            temperature=temperature,
            timestamp_unix=self.current_time,
            oil_pressure_psi=sensors["oil_pressure_psi"],
            vibration_mms=sensors["vibration_mms"],
            voltage_v=sensors["voltage_v"],
            rpm=sensors["rpm"],
        )
        
        # Convert RUL to hours for scheduler
        rul_hours = None
        if agent_result.get("estimated_rul_seconds"):
            rul_hours = agent_result["estimated_rul_seconds"] / 3600.0
        
        # Update scheduler with elapsed time and DTCs
        scheduled_tasks = self.scheduler.update(
            elapsed_hours=elapsed_hours,
            active_dtcs=agent_result.get("active_dtcs", []),
            rul_hours=rul_hours,
        )
        
        # Get ML insights
        ml_insights = self._get_ml_insights(
            temperature=temperature,
            rpm=sensors["rpm"],
            oil_pressure_psi=sensors["oil_pressure_psi"],
            vibration_mms=sensors["vibration_mms"],
        )
        
        # Track decisions
        self._track_decisions(agent_result, ml_insights, scheduled_tasks, temperature)
        
        # Get recent decisions for response
        recent_decisions = self.decision_tracker.get_decisions(limit=5)
        
        # Build comprehensive response
        response = {
            # Timestamps
            "timestamp": self.current_time,
            "simulation_time": self.simulation_time,
            "tick_count": self.tick_count,
            
            # Sensor data
            "temperature": round(temperature, 1),
            "rpm": sensors["rpm"],
            "oil_pressure_psi": round(sensors["oil_pressure_psi"], 1),
            "vibration_mms": round(sensors["vibration_mms"], 1),
            "voltage_v": round(sensors["voltage_v"], 2),
            
            # Agent state (6-state FSM)
            "state": agent_result["state"],
            "state_changed": agent_result["changed"],
            "alert_message": agent_result["alert_message"],
            "severity": agent_result.get("severity", "INFO"),
            
            # DTCs
            "dtcs": agent_result.get("dtcs", []),
            "active_dtcs": agent_result.get("active_dtcs", []),
            
            # Drift and RUL
            "drift_rate_per_min": agent_result.get("drift_rate_per_min", 0.0),
            "estimated_rul_seconds": agent_result.get("estimated_rul_seconds"),
            "estimated_rul_display": agent_result.get("estimated_rul_display", "N/A"),
            
            # Dynamic scheduled tasks (sorted by priority)
            "scheduled_tasks": scheduled_tasks[:5],  # Top 5 tasks
            "scheduler_stats": self.scheduler.get_stats(),
            
            # ML insights
            "ml_insights": ml_insights,
            
            # Recent decisions
            "recent_decisions": recent_decisions,
            "decision_stats": self.decision_tracker.get_stats(),
        }
        
        return response
    
    def _track_decisions(
        self,
        agent_result: Dict[str, Any],
        ml_insights: Dict[str, Any],
        scheduled_tasks: list,
        temperature: float,
    ):
        """Track all decisions made this tick."""
        tracker = self.decision_tracker
        
        # Track state changes
        if agent_result.get("changed"):
            tracker.log_state_change(
                tick_count=self.tick_count,
                previous_state=agent_result.get("previous_state", "UNKNOWN"),
                new_state=agent_result.get("state"),
                trigger_value=temperature,
                trigger_threshold=agent_result.get("threshold", 221.0),
                severity=agent_result.get("severity", "INFO"),
            )
        
        # Track new DTCs
        for dtc in agent_result.get("dtcs", []):
            if dtc.get("just_triggered"):
                tracker.log_dtc_trigger(
                    tick_count=self.tick_count,
                    dtc_code=dtc.get("code", ""),
                    dtc_name=dtc.get("name", ""),
                    severity=dtc.get("severity", "MEDIUM"),
                    trigger_value=dtc.get("trigger_value", 0),
                    threshold=dtc.get("threshold", 0),
                    action=dtc.get("action", ""),
                )
        
        # Track ML fault detection (only when detected)
        if ml_insights.get("fault_detection", {}).get("detected"):
            tracker.log_ml_prediction(
                tick_count=self.tick_count,
                prediction_type="Fault Detection",
                result=True,
                confidence=ml_insights["fault_detection"].get("confidence", 0),
                details=f"ML model detected potential fault with {ml_insights['fault_detection'].get('confidence', 0)*100:.1f}% confidence",
            )
        
        # Track vibration anomaly
        if ml_insights.get("vibration_anomaly", {}).get("detected"):
            tracker.log_ml_prediction(
                tick_count=self.tick_count,
                prediction_type="Vibration Anomaly",
                result=True,
                confidence=abs(ml_insights["vibration_anomaly"].get("score", 0)),
                details=f"Abnormal vibration pattern detected. Anomaly score: {ml_insights['vibration_anomaly'].get('score', 0):.2f}",
            )
        
        # Track RUL when estimated (every 10 ticks to avoid spam)
        rul_seconds = agent_result.get("estimated_rul_seconds")
        if rul_seconds and self.tick_count % 10 == 0:
            tracker.log_rul_estimate(
                tick_count=self.tick_count,
                rul_seconds=rul_seconds,
                drift_rate=agent_result.get("drift_rate_per_min", 0),
                current_temp=temperature,
            )
        
        # Track high drift rate
        drift_rate = agent_result.get("drift_rate_per_min", 0)
        if drift_rate > 2.0:  # Alert if drifting more than 2°F/min
            tracker.log_drift_alert(
                tick_count=self.tick_count,
                drift_rate=drift_rate,
                threshold=2.0,
            )

    def _generate_sensor_data(self, temperature: float) -> Dict[str, Any]:
        """
        Generate correlated sensor data based on temperature and tick count.
        
        Models physical relationships:
        - RPM: Simulated engine speed
        - Oil Pressure: Correlates with RPM and temperature (viscosity)
        - Vibration: Correlates with RPM and fault conditions
        - Voltage: Correlates with RPM (alternator)
        """
        # RPM simulation (500-3000 range, varies with time)
        base_rpm = 1500
        rpm_variation = 500 * math.sin(self.tick_count * 0.1)
        rpm = int(base_rpm + rpm_variation + (self.tick_count * 2) % 500)
        rpm = max(500, min(3000, rpm))
        
        # Oil pressure: P = f(RPM, Temperature)
        # Higher RPM = higher pressure, higher temp = lower viscosity = lower pressure
        base_pressure = 40.0
        rpm_factor = (rpm / 3000) * 20  # 0-20 PSI from RPM
        temp_factor = (temperature - 70) * -0.1  # Higher temp = lower pressure
        fault_factor = self.fault_magnitude * 0.5 if self.fault_injection_enabled else 0
        oil_pressure_psi = base_pressure + rpm_factor + temp_factor - fault_factor
        oil_pressure_psi = max(10.0, min(70.0, oil_pressure_psi))
        
        # Vibration: V = sqrt(BaseVib² + TempEffect² + RPMEffect² + FaultEffect²)
        base_vibration = 5.0
        temp_effect = abs((temperature - 160) * 0.03)  # Deviation from optimal
        rpm_effect = (rpm / 3000) * 6
        fault_effect = self.fault_magnitude * 0.3 if self.fault_injection_enabled else 0
        vibration_mms = math.sqrt(
            base_vibration**2 + temp_effect**2 + rpm_effect**2 + fault_effect**2
        )
        vibration_mms = max(2.0, min(40.0, vibration_mms))
        
        # Voltage: Higher RPM = higher alternator output
        base_voltage = 12.6
        rpm_voltage = (rpm / 3000) * 1.8  # 0-1.8V from RPM
        temp_voltage = (temperature - 100) * -0.002  # Minor temp effect
        voltage_v = base_voltage + rpm_voltage + temp_voltage
        voltage_v = max(10.5, min(15.0, voltage_v))
        
        return {
            "rpm": rpm,
            "oil_pressure_psi": oil_pressure_psi,
            "vibration_mms": vibration_mms,
            "voltage_v": voltage_v,
        }
    
    def _get_ml_insights(
        self,
        temperature: float,
        rpm: int,
        oil_pressure_psi: float,
        vibration_mms: float,
    ) -> Dict[str, Any]:
        """Get ML predictions with graceful fallback."""
        # Always return a valid structure
        default_insights = {
            "fault_detection": {
                "detected": False,
                "confidence": 0.0,
                "inference_time": 0.0,
            },
            "vibration_anomaly": {
                "detected": False,
                "score": 0.0,
                "inference_time": 0.0,
            },
            "pressure_prediction": {
                "predicted_pressure": oil_pressure_psi,
                "actual_pressure": oil_pressure_psi,
                "confidence": 0.85,
                "inference_time": 0.0,
            },
        }
        
        # Try to load ML trainer
        if not self._ml_load_attempted:
            self._ml_load_attempted = True
            try:
                from ml_training_kaggle import MLModelTrainer
                self._ml_trainer = MLModelTrainer()
                self._ml_trainer.load_all_models()
            except Exception as e:
                # ML trainer failed to load - will use synthetic fallbacks
                self._ml_trainer = None
        
        if not self._ml_trainer:
            return default_insights
        
        try:
            trainer = self._ml_trainer
            
            # Fault detection
            start = time.time()
            fault_pred = trainer.predict_fault(
                rpm=rpm,
                pressure=oil_pressure_psi,
                temp=temperature,
                vib=vibration_mms
            )
            fault_time = (time.time() - start) * 1000
            
            # Vibration anomaly
            start = time.time()
            vib_pred = trainer.detect_vibration_anomaly(
                bearing_1=vibration_mms,
                bearing_2=vibration_mms * 0.9
            )
            vib_time = (time.time() - start) * 1000
            
            # Pressure prediction
            start = time.time()
            pressure_pred = trainer.predict_pressure(flow_rate=rpm / 100)
            pressure_time = (time.time() - start) * 1000
            
            return {
                "fault_detection": {
                    "detected": fault_pred.get("fault", False),
                    "confidence": fault_pred.get("confidence", 0.0),
                    "inference_time": round(fault_time, 2),
                },
                "vibration_anomaly": {
                    "detected": vib_pred.get("anomaly", False),
                    "score": vib_pred.get("score", 0.0),
                    "inference_time": round(vib_time, 2),
                },
                "pressure_prediction": {
                    "predicted_pressure": pressure_pred.get("predicted_pressure", oil_pressure_psi),
                    "actual_pressure": oil_pressure_psi,
                    "confidence": pressure_pred.get("confidence", 0.85),
                    "inference_time": round(pressure_time, 2),
                },
            }
        except Exception as e:
            print(f"⚠️  ML prediction error: {e}")
            return default_insights
    
    def set_fault_injection(self, enabled: bool, magnitude: float = 0.0) -> None:
        """Enable or disable fault injection mode."""
        self.fault_injection_enabled = enabled
        self.fault_magnitude = magnitude
        self.simulator.set_fault_mode(enabled, magnitude)
    
    def reset_simulation(self) -> None:
        """Reset the simulation to initial state."""
        self.simulator.reset()
        self.agent = YSMAI_EnhancedAgent()
        self.scheduler.clear()
        self.decision_tracker.clear()
        
        self.current_time = time.time()
        self.simulation_start_time = self.current_time
        self.simulation_time = 0.0
        self.simulation_hours = 0.0
        self.tick_count = 0
        
        self.fault_injection_enabled = False
        self.fault_magnitude = 0.0
    
    def get_decisions(
        self,
        limit: int = 50,
        decision_type: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> list:
        """Get decisions with optional filtering."""
        return self.decision_tracker.get_decisions(
            limit=limit,
            decision_type=decision_type,
            category=category,
            severity=severity,
        )
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of all decisions and system state."""
        report = self.decision_tracker.generate_report()
        
        # Get agent state safely
        agent_state = "UNKNOWN"
        if hasattr(self.agent, 'current_state'):
            cs = self.agent.current_state
            if hasattr(cs, 'value'):
                agent_state = cs.value
            else:
                agent_state = str(cs)
        
        # Add current system state to report
        report["current_state"] = {
            "tick_count": self.tick_count,
            "simulation_time": self.simulation_time,
            "simulation_hours": self.simulation_hours,
            "agent_state": agent_state,
            "fault_injection_enabled": self.fault_injection_enabled,
            "fault_magnitude": self.fault_magnitude,
        }
        
        # Add scheduler state
        report["scheduler_state"] = self.scheduler.get_stats()
        
        return report
    
    def get_state(self) -> Dict[str, Any]:
        """Get full controller state for debugging."""
        return {
            "tick_count": self.tick_count,
            "simulation_time": self.simulation_time,
            "simulation_hours": self.simulation_hours,
            "agent_state": self.agent.get_debug_state(),
            "scheduler_stats": self.scheduler.get_stats(),
            "fault_injection": {
                "enabled": self.fault_injection_enabled,
                "magnitude": self.fault_magnitude,
            },
        }
    
    @staticmethod
    def to_json(response: Dict[str, Any]) -> str:
        """Convert response to JSON string."""
        return json.dumps(response, indent=2, default=str)


# Backwards compatibility alias
SimulationController = EnhancedSimulationController
