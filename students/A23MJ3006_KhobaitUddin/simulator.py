"""
TemperatureSimulator Module

Simulates HVAC system temperature behavior with warmup phase, drift, and fault injection.
"""

import time
import random
from typing import Optional


class TemperatureSimulator:
    """
    Simulates temperature behavior in an HVAC system.
    
    Behavior:
    - Warmup phase: ramps from initial_temp at constant rate for warmup_duration_sec
    - Drift phase: after warmup, adds ±drift_rate per second (simulating aging)
    - Fault mode: injects random spikes/dips when enabled
    """
    
    def __init__(
        self,
        initial_temp: float = 70.0,
        target_operating_temp: float = 180.0,  # Marine engine normal operating temp (°F)
        warmup_duration_sec: float = 10.0,     # Time to reach operating temp
        drift_rate: float = 0.5
    ):
        """
        Initialize the TemperatureSimulator.
        
        Args:
            initial_temp: Starting temperature in °F (default: 70, ambient)
            target_operating_temp: Normal operating temperature (default: 180°F, marine engine)
            warmup_duration_sec: Duration of warmup phase in seconds (default: 10)
            drift_rate: Temperature drift rate in °F per second after warmup (default: 0.5)
        """
        self.initial_temp = initial_temp
        self.target_operating_temp = target_operating_temp
        self.warmup_duration_sec = warmup_duration_sec
        self.drift_rate = drift_rate
        
        # State variables
        self.current_temp = initial_temp
        self.elapsed_time = 0.0
        self.fault_injection_enabled = False
        self.fault_magnitude = 0.0
        
        # Random drift direction (positive or negative)
        self.drift_direction = random.choice([1, -1])
    
    def tick(self, elapsed_time_sec: float) -> float:
        """
        Update temperature state and return current temperature.
        
        Args:
            elapsed_time_sec: Time elapsed since last tick (or initialization)
        
        Returns:
            Current temperature in °F (range 50–120)
        """
        import math
        
        self.elapsed_time += elapsed_time_sec
        
        if self.elapsed_time <= self.warmup_duration_sec:
            # Warmup phase: exponential decay T(t) = T_amb + (T_op - T_amb) * (1 - e^(-kt))
            # Where T_amb = initial_temp, T_op = target operating temp, k = decay constant
            T_amb = self.initial_temp
            T_op = self.target_operating_temp  # Target operating temp (e.g., 180°F for marine engine)
            k = 3.0 / self.warmup_duration_sec  # Decay constant ensures ~95% reached in warmup_duration
            self.current_temp = T_amb + (T_op - T_amb) * (1 - math.exp(-k * self.elapsed_time))
        else:
            # Drift phase: apply drift after warmup
            drift_amount = self.drift_rate * self.drift_direction * elapsed_time_sec
            self.current_temp += drift_amount
        
        # Apply fault injection if enabled
        if self.fault_injection_enabled:
            # Random spike or dip
            fault_spike = random.uniform(-self.fault_magnitude, self.fault_magnitude)
            self.current_temp += fault_spike
        
        # Clamp temperature to realistic range (marine engine: 50-250°F)
        self.current_temp = max(50.0, min(250.0, self.current_temp))
        
        return self.current_temp
    
    def set_fault_mode(self, enabled: bool, magnitude: float = 0.0) -> None:
        """
        Enable or disable fault injection mode.
        
        Args:
            enabled: Whether fault injection is active
            magnitude: Max magnitude of temperature spikes/dips in °F
        """
        self.fault_injection_enabled = enabled
        self.fault_magnitude = magnitude
    
    def reset(self) -> None:
        """Reset the simulator to initial state."""
        self.current_temp = self.initial_temp
        self.elapsed_time = 0.0
        self.fault_injection_enabled = False
        self.fault_magnitude = 0.0
        self.drift_direction = random.choice([1, -1])
    
    def get_state(self) -> dict:
        """
        Get current simulator state (for debugging).
        
        Returns:
            Dictionary with current state values
        """
        return {
            "current_temp": self.current_temp,
            "elapsed_time": self.elapsed_time,
            "warmup_phase": self.elapsed_time <= self.warmup_duration_sec,
            "fault_enabled": self.fault_injection_enabled,
            "fault_magnitude": self.fault_magnitude,
        }
