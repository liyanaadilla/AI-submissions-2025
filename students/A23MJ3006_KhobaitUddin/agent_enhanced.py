"""
YSMAI Enhanced Agent Module

6-State FSM with Yanmar DTC codes, drift detection, and RUL estimation.
States: S0_IDLE → S1_WARMUP → S2_NORMAL → S3_WARNING → S4_CRITICAL → S5_SHUTDOWN

DTCs Implemented (Yanmar/OBD-II compatible):
- P0217: Engine Coolant Over Temperature
- P0117: Engine Coolant Temperature Circuit Low
- P0118: Engine Coolant Temperature Circuit High
- P0562: System Voltage Low
- P0563: System Voltage High
- P0520: Engine Oil Pressure Sensor Circuit
- P0521: Engine Oil Pressure Sensor Range/Performance
- P0522: Engine Oil Pressure Sensor Low
- P2263: Turbo/Supercharger Boost System Performance (Vibration)
"""

import time
from typing import Dict, Optional, List, Tuple
from collections import deque


class YanmarDTCCodes:
    """Yanmar Diagnostic Trouble Codes mapping."""
    
    # Temperature related
    P0217 = ("P0217", "Engine Coolant Over Temperature")
    P0118 = ("P0118", "Engine Coolant Temperature Circuit High")
    P0117 = ("P0117", "Engine Coolant Temperature Circuit Low")
    
    # Voltage related
    P0562 = ("P0562", "System Voltage Low")
    P0563 = ("P0563", "System Voltage High")
    
    # Oil pressure related
    P0520 = ("P0520", "Engine Oil Pressure Sensor Circuit")
    P0521 = ("P0521", "Engine Oil Pressure Sensor Range/Performance")
    P0522 = ("P0522", "Engine Oil Pressure Sensor Low")
    P0523 = ("P0523", "Engine Oil Pressure Sensor High")
    
    # Vibration/turbo related
    P2263 = ("P2263", "Turbo Boost System Performance - Excessive Vibration")


class YSMAI_EnhancedAgent:
    """
    Enhanced HVAC monitoring agent with 6-state FSM and Yanmar DTCs.
    
    States (per YSMAI_Project_Planning.txt):
    - S0_IDLE: Engine off, standby
    - S1_WARMUP: Engine starting, temperature rising
    - S2_NORMAL: Normal operation
    - S3_WARNING: Threshold approaching
    - S4_CRITICAL: Threshold exceeded
    - S5_SHUTDOWN: Emergency shutdown triggered
    
    Features:
    - Multi-sensor monitoring (temp, pressure, vibration, voltage)
    - Drift rate analysis (dT/dt) with sliding window
    - Remaining Useful Life (RUL) estimation
    - Yanmar DTC code generation
    - Debounce logic for state transitions
    """
    
    # State constants (6-state FSM)
    S0_IDLE = "IDLE"
    S1_WARMUP = "WARMUP"
    S2_NORMAL = "NORMAL"
    S3_WARNING = "WARNING"
    S4_CRITICAL = "CRITICAL"
    S5_SHUTDOWN = "SHUTDOWN"
    
    # State order for progression tracking
    STATE_ORDER = [S0_IDLE, S1_WARMUP, S2_NORMAL, S3_WARNING, S4_CRITICAL, S5_SHUTDOWN]
    
    # Severity mapping for UI
    STATE_SEVERITY = {
        S0_IDLE: "INFO",
        S1_WARMUP: "INFO",
        S2_NORMAL: "INFO",
        S3_WARNING: "WARNING",
        S4_CRITICAL: "CRITICAL",
        S5_SHUTDOWN: "CRITICAL",
    }
    
    def __init__(
        self,
        # Temperature thresholds (in °F for frontend compatibility)
        temp_warmup_target: float = 160.0,      # 71°C - thermostat opens
        temp_normal_max: float = 203.0,         # 95°C - normal operating max
        temp_warning: float = 221.0,            # 105°C - warning threshold
        temp_critical: float = 226.0,           # 108°C - critical alarm
        temp_shutdown: float = 239.0,           # 115°C - limp mode/shutdown
        temp_low: float = 50.0,                 # Below normal
        # Oil pressure thresholds (PSI)
        oil_pressure_low: float = 25.0,         # Low oil pressure warning
        oil_pressure_critical: float = 15.0,    # Critical low
        # Vibration thresholds (mm/s RMS per ISO 10816-6)
        vibration_warning: float = 18.0,        # Warning
        vibration_critical: float = 28.0,       # Critical
        # Voltage thresholds
        voltage_low: float = 11.5,
        voltage_critical_low: float = 10.5,
        voltage_high: float = 14.8,
        # Timing
        debounce_sec: float = 1.5,
        drift_window_size: int = 10,            # Samples for drift calculation
    ):
        """Initialize enhanced agent with Yanmar-spec thresholds."""
        # Temperature thresholds
        self.temp_warmup_target = temp_warmup_target
        self.temp_normal_max = temp_normal_max
        self.temp_warning = temp_warning
        self.temp_critical = temp_critical
        self.temp_shutdown = temp_shutdown
        self.temp_low = temp_low
        
        # Oil pressure thresholds
        self.oil_pressure_low = oil_pressure_low
        self.oil_pressure_critical = oil_pressure_critical
        
        # Vibration thresholds (ISO 10816-6)
        self.vibration_warning = vibration_warning
        self.vibration_critical = vibration_critical
        
        # Voltage thresholds
        self.voltage_low = voltage_low
        self.voltage_critical_low = voltage_critical_low
        self.voltage_high = voltage_high
        
        # Timing
        self.debounce_sec = debounce_sec
        self.drift_window_size = drift_window_size
        
        # State tracking
        self.current_state = self.S0_IDLE
        self.last_state = self.S0_IDLE
        self.state_timestamp = time.time()
        self.last_transition_time = time.time()
        
        # Debounce tracking
        self.pending_state = None
        self.pending_timestamp = None
        
        # Active DTCs
        self.active_dtcs: List[Tuple[str, str, float]] = []  # (code, desc, timestamp)
        
        # Drift analysis (sliding window)
        self.temp_history: deque = deque(maxlen=drift_window_size)
        self.time_history: deque = deque(maxlen=drift_window_size)
        
        # Sensor values cache for multi-sensor analysis
        self.last_sensors = {
            "temperature": 70.0,
            "oil_pressure_psi": 40.0,
            "vibration_mms": 5.0,
            "voltage_v": 13.2,
            "rpm": 0,
        }
        
        # RUL estimation
        self.estimated_rul_seconds: Optional[float] = None
        self.drift_rate: float = 0.0  # °F per second
    
    def update(
        self,
        temperature: float,
        timestamp_unix: float,
        oil_pressure_psi: float = 40.0,
        vibration_mms: float = 5.0,
        voltage_v: float = 13.2,
        rpm: int = 0,
    ) -> Dict:
        """
        Update agent state based on all sensor inputs.
        
        Args:
            temperature: Current temperature (°F)
            timestamp_unix: Current unix timestamp
            oil_pressure_psi: Oil pressure (PSI)
            vibration_mms: Vibration RMS (mm/s)
            voltage_v: System voltage (V)
            rpm: Engine RPM
        
        Returns:
            Dictionary with state info, DTCs, drift rate, RUL
        """
        self.last_state = self.current_state
        state_changed = False
        alert_message = None
        new_dtcs = []
        
        # Cache sensor values
        self.last_sensors = {
            "temperature": temperature,
            "oil_pressure_psi": oil_pressure_psi,
            "vibration_mms": vibration_mms,
            "voltage_v": voltage_v,
            "rpm": rpm,
        }
        
        # Update drift tracking
        self._update_drift_tracking(temperature, timestamp_unix)
        
        # Determine desired state and check for DTCs
        desired_state, detected_dtcs = self._compute_desired_state_and_dtcs(
            temperature, oil_pressure_psi, vibration_mms, voltage_v, rpm
        )
        
        # Add new DTCs
        for dtc_code, dtc_desc in detected_dtcs:
            if not any(d[0] == dtc_code for d in self.active_dtcs):
                self.active_dtcs.append((dtc_code, dtc_desc, timestamp_unix))
                new_dtcs.append((dtc_code, dtc_desc))
        
        # State transition with debounce
        if desired_state == self.current_state:
            self.pending_state = None
            self.pending_timestamp = None
        else:
            if self.pending_state != desired_state:
                # New pending state
                self.pending_state = desired_state
                self.pending_timestamp = timestamp_unix
            else:
                # Check debounce
                time_in_pending = timestamp_unix - self.pending_timestamp
                if time_in_pending >= self.debounce_sec:
                    self.current_state = desired_state
                    self.state_timestamp = timestamp_unix
                    self.last_transition_time = timestamp_unix
                    state_changed = True
                    alert_message = self._generate_alert_message(
                        self.current_state, new_dtcs, temperature
                    )
                    self.pending_state = None
                    self.pending_timestamp = None
        
        # Calculate RUL if in warning/critical state
        self._update_rul_estimate(temperature)
        
        return {
            "state": self.current_state.value if hasattr(self.current_state, 'value') else str(self.current_state),
            "previous_state": self.last_state.value if hasattr(self.last_state, 'value') else str(self.last_state),
            "changed": state_changed,
            "alert_message": alert_message,
            "timestamp": timestamp_unix,
            "threshold": self.temp_warning if self.current_state == self.S3_WARNING else self.temp_critical,
            "severity": self.STATE_SEVERITY.get(self.current_state, "INFO"),
            "dtcs": [{"code": d[0], "description": d[1], "just_triggered": True, "severity": "HIGH", "trigger_value": temperature, "threshold": self.temp_warning, "action": "Check cooling system"} for d in new_dtcs],
            "active_dtcs": [
                {"code": d[0], "description": d[1], "timestamp": d[2]}
                for d in self.active_dtcs
            ],
            "drift_rate_per_min": round(self.drift_rate * 60, 2),  # °F per minute
            "estimated_rul_seconds": self.estimated_rul_seconds,
            "estimated_rul_display": self._format_rul(self.estimated_rul_seconds),
        }
    
    def _update_drift_tracking(self, temperature: float, timestamp: float) -> None:
        """Track temperature history for drift calculation."""
        self.temp_history.append(temperature)
        self.time_history.append(timestamp)
        
        if len(self.temp_history) >= 2:
            # Calculate drift rate (linear regression slope)
            temps = list(self.temp_history)
            times = list(self.time_history)
            
            n = len(temps)
            sum_t = sum(times)
            sum_temp = sum(temps)
            sum_t_temp = sum(t * temp for t, temp in zip(times, temps))
            sum_t_sq = sum(t * t for t in times)
            
            denominator = n * sum_t_sq - sum_t * sum_t
            if abs(denominator) > 1e-10:
                self.drift_rate = (n * sum_t_temp - sum_t * sum_temp) / denominator
            else:
                self.drift_rate = 0.0
    
    def _update_rul_estimate(self, temperature: float) -> None:
        """Estimate Remaining Useful Life based on drift rate."""
        if self.drift_rate > 0.001:  # Only if temperature is rising
            # Time to reach critical threshold
            temp_to_critical = self.temp_critical - temperature
            if temp_to_critical > 0:
                self.estimated_rul_seconds = temp_to_critical / self.drift_rate
            else:
                self.estimated_rul_seconds = 0
        else:
            self.estimated_rul_seconds = None  # Not applicable
    
    def _format_rul(self, seconds: Optional[float]) -> str:
        """Format RUL seconds to human-readable string."""
        if seconds is None:
            return "N/A"
        if seconds <= 0:
            return "IMMINENT"
        if seconds < 60:
            return f"{int(seconds)}s"
        if seconds < 3600:
            return f"{int(seconds / 60)}m {int(seconds % 60)}s"
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"
    
    def _compute_desired_state_and_dtcs(
        self,
        temp: float,
        oil_pressure: float,
        vibration: float,
        voltage: float,
        rpm: int,
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Compute desired state and detect any DTC conditions.
        
        Returns:
            (desired_state, list of (dtc_code, dtc_description))
        """
        dtcs = []
        state = self.S2_NORMAL  # Default
        
        def escalate_state(new_state: str) -> str:
            """Escalate to higher severity state."""
            current_idx = self.STATE_ORDER.index(state)
            new_idx = self.STATE_ORDER.index(new_state)
            return self.STATE_ORDER[max(current_idx, new_idx)]
        
        # === TEMPERATURE ANALYSIS ===
        if temp >= self.temp_shutdown:
            state = self.S5_SHUTDOWN
            dtcs.append(YanmarDTCCodes.P0217)
        elif temp >= self.temp_critical:
            state = self.S4_CRITICAL
            dtcs.append(YanmarDTCCodes.P0217)
        elif temp >= self.temp_warning:
            state = self.S3_WARNING
            dtcs.append(YanmarDTCCodes.P0118)
        elif temp < self.temp_low:
            if rpm > 0:
                state = self.S1_WARMUP
            else:
                state = self.S0_IDLE
            if temp < 32:  # Freezing
                dtcs.append(YanmarDTCCodes.P0117)
        elif temp < self.temp_warmup_target and rpm > 0:
            state = self.S1_WARMUP
        
        # === OIL PRESSURE ANALYSIS ===
        if rpm > 500:  # Only check when engine running
            if oil_pressure < self.oil_pressure_critical:
                state = escalate_state(self.S4_CRITICAL)
                dtcs.append(YanmarDTCCodes.P0522)
            elif oil_pressure < self.oil_pressure_low:
                state = escalate_state(self.S3_WARNING)
                dtcs.append(YanmarDTCCodes.P0521)
        
        # === VIBRATION ANALYSIS ===
        if vibration >= self.vibration_critical:
            state = escalate_state(self.S4_CRITICAL)
            dtcs.append(YanmarDTCCodes.P2263)
        elif vibration >= self.vibration_warning:
            state = escalate_state(self.S3_WARNING)
            dtcs.append(YanmarDTCCodes.P2263)
        
        # === VOLTAGE ANALYSIS ===
        if voltage < self.voltage_critical_low:
            state = escalate_state(self.S4_CRITICAL)
            dtcs.append(YanmarDTCCodes.P0562)
        elif voltage < self.voltage_low:
            state = escalate_state(self.S3_WARNING)
            dtcs.append(YanmarDTCCodes.P0562)
        elif voltage > self.voltage_high:
            state = escalate_state(self.S3_WARNING)
            dtcs.append(YanmarDTCCodes.P0563)
        
        # Handle IDLE state based on RPM
        if rpm == 0 and state == self.S2_NORMAL:
            state = self.S0_IDLE
        
        return state, dtcs
    
    def _generate_alert_message(
        self,
        state: str,
        new_dtcs: List[Tuple[str, str]],
        temperature: float,
    ) -> Optional[str]:
        """Generate alert message with DTC codes."""
        if state in [self.S2_NORMAL, self.S0_IDLE]:
            return None
        
        # Build message with DTCs
        dtc_str = ""
        if new_dtcs:
            codes = ", ".join([f"{d[0]}" for d in new_dtcs])
            dtc_str = f" [DTCs: {codes}]"
        
        messages = {
            self.S1_WARMUP: f"Engine warmup in progress. Current: {temperature:.1f}°F",
            self.S3_WARNING: f"⚠️ WARNING: Threshold approaching.{dtc_str} Temp: {temperature:.1f}°F",
            self.S4_CRITICAL: f"🚨 CRITICAL: Immediate attention required!{dtc_str} Temp: {temperature:.1f}°F",
            self.S5_SHUTDOWN: f"🛑 SHUTDOWN: Emergency stop triggered!{dtc_str} Temp: {temperature:.1f}°F",
        }
        
        return messages.get(state, f"State changed to {state}")
    
    def clear_dtc(self, dtc_code: str) -> bool:
        """Clear a specific DTC code."""
        initial_len = len(self.active_dtcs)
        self.active_dtcs = [d for d in self.active_dtcs if d[0] != dtc_code]
        return len(self.active_dtcs) < initial_len
    
    def clear_all_dtcs(self) -> int:
        """Clear all active DTCs. Returns count cleared."""
        count = len(self.active_dtcs)
        self.active_dtcs = []
        return count
    
    def get_state(self) -> str:
        """Get current state."""
        return self.current_state
    
    def get_timestamp(self) -> float:
        """Get timestamp of last state transition."""
        return self.last_transition_time
    
    def get_debug_state(self) -> Dict:
        """Get full agent state for debugging."""
        return {
            "current_state": self.current_state,
            "last_state": self.last_state,
            "state_timestamp": self.state_timestamp,
            "last_transition_time": self.last_transition_time,
            "pending_state": self.pending_state,
            "active_dtcs_count": len(self.active_dtcs),
            "drift_rate_per_min": round(self.drift_rate * 60, 2),
            "estimated_rul_seconds": self.estimated_rul_seconds,
            "last_sensors": self.last_sensors,
        }
