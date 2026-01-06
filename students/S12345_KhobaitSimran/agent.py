"""
YSMAI_Agent Module

State machine for monitoring temperature and managing alert states.
Features 3-state FSM with debounce logic and timestamp tracking.
"""

import time
from typing import Dict, Optional


class YSMAI_Agent:
    """
    HVAC monitoring agent with 3-state finite state machine.
    
    States: NORMAL, ALERT_HIGH, ALERT_LOW
    
    Features:
    - Debounce: state transitions only if condition persists for debounce_sec
    - Timestamp tracking: tracks state changes with unix timestamps
    - Alert messages: generated only on state transitions
    """
    
    # State constants
    STATE_NORMAL = "NORMAL"
    STATE_ALERT_HIGH = "ALERT_HIGH"
    STATE_ALERT_LOW = "ALERT_LOW"
    
    def __init__(
        self,
        threshold_high: float = 85.0,
        threshold_low: float = 50.0,
        debounce_sec: float = 1.5
    ):
        """
        Initialize the YSMAI_Agent.
        
        Args:
            threshold_high: High temperature threshold in °F (default: 85)
            threshold_low: Low temperature threshold in °F (default: 50)
            debounce_sec: Debounce duration in seconds (default: 1.5)
        """
        self.threshold_high = threshold_high
        self.threshold_low = threshold_low
        self.debounce_sec = debounce_sec
        
        # State tracking
        self.current_state = self.STATE_NORMAL
        self.last_state = self.STATE_NORMAL
        self.state_timestamp = time.time()  # When current state was entered
        self.last_transition_time = time.time()  # Unix timestamp of last transition
        
        # Debounce tracking: temp that triggered the pending state change
        self.pending_state = None
        self.pending_timestamp = None
    
    def update(
        self,
        temp: float,
        timestamp_unix: float
    ) -> Dict:
        """
        Update agent state based on current temperature.
        
        Args:
            temp: Current temperature in °F
            timestamp_unix: Current unix timestamp
        
        Returns:
            Dictionary with state info:
            {
                "state": str (NORMAL|ALERT_HIGH|ALERT_LOW),
                "changed": bool (True if state changed this tick),
                "alert_message": str or None,
                "timestamp": float (unix timestamp)
            }
        """
        self.last_state = self.current_state
        state_changed = False
        alert_message = None
        
        # Determine what state we should be in based on temperature
        desired_state = self._compute_desired_state(temp)
        
        # If desired state matches current state, clear pending state
        if desired_state == self.current_state:
            self.pending_state = None
            self.pending_timestamp = None
        else:
            # Transition needed; check debounce
            if self.pending_state is None:
                # First time we've seen this transition
                self.pending_state = desired_state
                self.pending_timestamp = timestamp_unix
            else:
                # Already pending; check if debounce has expired
                time_in_pending = timestamp_unix - self.pending_timestamp
                
                if time_in_pending >= self.debounce_sec:
                    # Debounce expired; make the transition
                    self.current_state = desired_state
                    self.state_timestamp = timestamp_unix
                    self.last_transition_time = timestamp_unix
                    state_changed = True
                    alert_message = self._generate_alert_message(self.current_state)
                    
                    # Clear pending state
                    self.pending_state = None
                    self.pending_timestamp = None
        
        return {
            "state": self.current_state,
            "changed": state_changed,
            "alert_message": alert_message,
            "timestamp": timestamp_unix,
        }
    
    def _compute_desired_state(self, temp: float) -> str:
        """
        Determine desired state based on temperature and thresholds.
        
        Uses hysteresis to prevent rapid state flicker.
        
        Args:
            temp: Current temperature in °F
        
        Returns:
            Desired state string
        """
        if temp > self.threshold_high:
            return self.STATE_ALERT_HIGH
        elif temp < self.threshold_low:
            return self.STATE_ALERT_LOW
        else:
            return self.STATE_NORMAL
    
    def _generate_alert_message(self, state: str) -> Optional[str]:
        """
        Generate human-readable alert message for state change.
        
        Args:
            state: Current state
        
        Returns:
            Alert message or None for NORMAL state
        """
        if state == self.STATE_ALERT_HIGH:
            return f"High temperature alert: {self.threshold_high}°F threshold exceeded"
        elif state == self.STATE_ALERT_LOW:
            return f"Low temperature alert: below {self.threshold_low}°F threshold"
        else:
            return None
    
    def get_state(self) -> str:
        """
        Get current state.
        
        Returns:
            Current state string
        """
        return self.current_state
    
    def get_timestamp(self) -> float:
        """
        Get timestamp of last state transition.
        
        Returns:
            Unix timestamp of last transition
        """
        return self.last_transition_time
    
    def get_debug_state(self) -> Dict:
        """
        Get full agent state for debugging.
        
        Returns:
            Dictionary with all state variables
        """
        return {
            "current_state": self.current_state,
            "last_state": self.last_state,
            "state_timestamp": self.state_timestamp,
            "last_transition_time": self.last_transition_time,
            "pending_state": self.pending_state,
            "pending_timestamp": self.pending_timestamp,
            "threshold_high": self.threshold_high,
            "threshold_low": self.threshold_low,
            "debounce_sec": self.debounce_sec,
        }
