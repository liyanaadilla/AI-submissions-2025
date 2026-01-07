"""
Decision Tracker Module

Tracks all agent decisions for reporting:
- State transitions
- DTC triggers
- Maintenance recommendations
- ML predictions
- Fault detections
"""

import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import deque


@dataclass
class Decision:
    """Represents a single agent decision."""
    decision_id: str
    timestamp: float
    tick_count: int
    decision_type: str  # STATE_CHANGE, DTC_TRIGGER, MAINTENANCE, ML_PREDICTION, FAULT_DETECTED
    category: str  # OPERATIONAL, DIAGNOSTIC, PREDICTIVE, SAFETY
    severity: str  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    title: str
    description: str
    trigger_value: Optional[float] = None
    trigger_threshold: Optional[float] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    dtc_codes: List[str] = field(default_factory=list)
    action_recommended: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result["timestamp_display"] = datetime.fromtimestamp(
            self.timestamp
        ).strftime("%Y-%m-%d %H:%M:%S")
        return result


class DecisionTracker:
    """
    Tracks all decisions made by the YSMAI agent.
    
    Features:
    - Rolling window of last N decisions
    - Category-based filtering
    - Report generation (JSON, summary)
    - Firebase integration ready
    """
    
    # Decision type constants
    TYPE_STATE_CHANGE = "STATE_CHANGE"
    TYPE_DTC_TRIGGER = "DTC_TRIGGER"
    TYPE_DTC_CLEARED = "DTC_CLEARED"
    TYPE_MAINTENANCE = "MAINTENANCE"
    TYPE_ML_PREDICTION = "ML_PREDICTION"
    TYPE_FAULT_DETECTED = "FAULT_DETECTED"
    TYPE_RUL_ESTIMATE = "RUL_ESTIMATE"
    TYPE_DRIFT_ALERT = "DRIFT_ALERT"
    
    # Category constants
    CAT_OPERATIONAL = "OPERATIONAL"
    CAT_DIAGNOSTIC = "DIAGNOSTIC"
    CAT_PREDICTIVE = "PREDICTIVE"
    CAT_SAFETY = "SAFETY"
    
    def __init__(self, max_decisions: int = 500):
        """
        Initialize the decision tracker.
        
        Args:
            max_decisions: Maximum decisions to keep in memory
        """
        self.decisions: deque = deque(maxlen=max_decisions)
        self.decision_counter = 0
        self.session_start = time.time()
        
        # Summary counters
        self.stats = {
            "total_decisions": 0,
            "by_type": {},
            "by_category": {},
            "by_severity": {},
            "state_transitions": 0,
            "dtcs_triggered": 0,
            "faults_detected": 0,
            "ml_predictions": 0,
        }
    
    def _generate_id(self) -> str:
        """Generate unique decision ID."""
        self.decision_counter += 1
        return f"DEC_{self.decision_counter:05d}"
    
    def _update_stats(self, decision: Decision):
        """Update statistics counters."""
        self.stats["total_decisions"] += 1
        
        # By type
        t = decision.decision_type
        self.stats["by_type"][t] = self.stats["by_type"].get(t, 0) + 1
        
        # By category
        c = decision.category
        self.stats["by_category"][c] = self.stats["by_category"].get(c, 0) + 1
        
        # By severity
        s = decision.severity
        self.stats["by_severity"][s] = self.stats["by_severity"].get(s, 0) + 1
        
        # Special counters
        if t == self.TYPE_STATE_CHANGE:
            self.stats["state_transitions"] += 1
        elif t == self.TYPE_DTC_TRIGGER:
            self.stats["dtcs_triggered"] += 1
        elif t == self.TYPE_FAULT_DETECTED:
            self.stats["faults_detected"] += 1
        elif t == self.TYPE_ML_PREDICTION:
            self.stats["ml_predictions"] += 1
    
    def log_state_change(
        self,
        tick_count: int,
        previous_state: str,
        new_state: str,
        trigger_value: float,
        trigger_threshold: float,
        severity: str = "INFO",
    ) -> Decision:
        """Log a state transition decision."""
        # Determine category based on severity
        category = self.CAT_OPERATIONAL
        if new_state in ["WARNING", "CRITICAL", "SHUTDOWN"]:
            category = self.CAT_SAFETY
        
        decision = Decision(
            decision_id=self._generate_id(),
            timestamp=time.time(),
            tick_count=tick_count,
            decision_type=self.TYPE_STATE_CHANGE,
            category=category,
            severity=severity,
            title=f"State: {previous_state} → {new_state}",
            description=f"Engine state changed from {previous_state} to {new_state} due to temperature {trigger_value:.1f}°F (threshold: {trigger_threshold:.1f}°F)",
            trigger_value=trigger_value,
            trigger_threshold=trigger_threshold,
            previous_state=previous_state,
            new_state=new_state,
            action_recommended=self._get_state_action(new_state),
        )
        
        self.decisions.append(decision)
        self._update_stats(decision)
        return decision
    
    def log_dtc_trigger(
        self,
        tick_count: int,
        dtc_code: str,
        dtc_name: str,
        severity: str,
        trigger_value: float,
        threshold: float,
        action: str,
    ) -> Decision:
        """Log a DTC trigger decision."""
        decision = Decision(
            decision_id=self._generate_id(),
            timestamp=time.time(),
            tick_count=tick_count,
            decision_type=self.TYPE_DTC_TRIGGER,
            category=self.CAT_DIAGNOSTIC,
            severity=severity,
            title=f"DTC {dtc_code}: {dtc_name}",
            description=f"Diagnostic trouble code {dtc_code} triggered. Value: {trigger_value:.2f}, Threshold: {threshold:.2f}",
            trigger_value=trigger_value,
            trigger_threshold=threshold,
            dtc_codes=[dtc_code],
            action_recommended=action,
        )
        
        self.decisions.append(decision)
        self._update_stats(decision)
        return decision
    
    def log_dtc_cleared(
        self,
        tick_count: int,
        dtc_code: str,
        dtc_name: str,
    ) -> Decision:
        """Log a DTC cleared decision."""
        decision = Decision(
            decision_id=self._generate_id(),
            timestamp=time.time(),
            tick_count=tick_count,
            decision_type=self.TYPE_DTC_CLEARED,
            category=self.CAT_DIAGNOSTIC,
            severity="INFO",
            title=f"DTC {dtc_code} Cleared",
            description=f"Diagnostic trouble code {dtc_code} ({dtc_name}) has been cleared - conditions returned to normal",
            dtc_codes=[dtc_code],
        )
        
        self.decisions.append(decision)
        self._update_stats(decision)
        return decision
    
    def log_maintenance_scheduled(
        self,
        tick_count: int,
        task_name: str,
        priority_score: float,
        due_in: str,
        triggered_by_dtc: Optional[str] = None,
    ) -> Decision:
        """Log a maintenance scheduling decision."""
        desc = f"Maintenance task '{task_name}' scheduled with priority {priority_score:.3f}. {due_in}"
        if triggered_by_dtc:
            desc += f" Triggered by DTC: {triggered_by_dtc}"
        
        decision = Decision(
            decision_id=self._generate_id(),
            timestamp=time.time(),
            tick_count=tick_count,
            decision_type=self.TYPE_MAINTENANCE,
            category=self.CAT_PREDICTIVE,
            severity="MEDIUM" if priority_score > 0.5 else "LOW",
            title=f"Maintenance: {task_name}",
            description=desc,
            confidence=priority_score,
            dtc_codes=[triggered_by_dtc] if triggered_by_dtc else [],
            action_recommended=f"Schedule {task_name} maintenance",
            metadata={"priority_score": priority_score, "due_in": due_in},
        )
        
        self.decisions.append(decision)
        self._update_stats(decision)
        return decision
    
    def log_ml_prediction(
        self,
        tick_count: int,
        prediction_type: str,
        result: bool,
        confidence: float,
        details: str,
    ) -> Decision:
        """Log an ML model prediction decision."""
        severity = "HIGH" if result else "INFO"
        
        decision = Decision(
            decision_id=self._generate_id(),
            timestamp=time.time(),
            tick_count=tick_count,
            decision_type=self.TYPE_ML_PREDICTION,
            category=self.CAT_PREDICTIVE,
            severity=severity,
            title=f"ML: {prediction_type}",
            description=details,
            confidence=confidence,
            metadata={"prediction_type": prediction_type, "result": result},
        )
        
        self.decisions.append(decision)
        self._update_stats(decision)
        return decision
    
    def log_rul_estimate(
        self,
        tick_count: int,
        rul_seconds: float,
        drift_rate: float,
        current_temp: float,
    ) -> Decision:
        """Log an RUL estimation decision."""
        rul_mins = rul_seconds / 60.0 if rul_seconds else 0
        severity = "CRITICAL" if rul_mins < 5 else "HIGH" if rul_mins < 15 else "MEDIUM" if rul_mins < 60 else "INFO"
        
        decision = Decision(
            decision_id=self._generate_id(),
            timestamp=time.time(),
            tick_count=tick_count,
            decision_type=self.TYPE_RUL_ESTIMATE,
            category=self.CAT_PREDICTIVE,
            severity=severity,
            title=f"RUL: {rul_mins:.1f} minutes",
            description=f"Estimated remaining useful life: {rul_mins:.1f} minutes. Drift rate: {drift_rate:.3f}°F/min. Current temp: {current_temp:.1f}°F",
            trigger_value=current_temp,
            confidence=0.85,
            action_recommended="Monitor closely" if rul_mins < 30 else None,
            metadata={
                "rul_seconds": rul_seconds,
                "rul_minutes": rul_mins,
                "drift_rate": drift_rate,
            },
        )
        
        self.decisions.append(decision)
        self._update_stats(decision)
        return decision
    
    def log_drift_alert(
        self,
        tick_count: int,
        drift_rate: float,
        threshold: float,
    ) -> Decision:
        """Log a drift rate alert decision."""
        decision = Decision(
            decision_id=self._generate_id(),
            timestamp=time.time(),
            tick_count=tick_count,
            decision_type=self.TYPE_DRIFT_ALERT,
            category=self.CAT_SAFETY,
            severity="HIGH",
            title=f"Drift Alert: {drift_rate:.2f}°F/min",
            description=f"Temperature drift rate ({drift_rate:.2f}°F/min) exceeds threshold ({threshold:.2f}°F/min). System may reach critical temperature soon.",
            trigger_value=drift_rate,
            trigger_threshold=threshold,
            action_recommended="Reduce load or enable cooling",
        )
        
        self.decisions.append(decision)
        self._update_stats(decision)
        return decision
    
    def _get_state_action(self, state: str) -> Optional[str]:
        """Get recommended action for a state."""
        actions = {
            "IDLE": "System ready to start",
            "WARMUP": "Allow engine to warm up before loading",
            "NORMAL": "System operating normally",
            "WARNING": "Reduce load and monitor temperature",
            "CRITICAL": "Reduce load immediately, prepare for shutdown",
            "SHUTDOWN": "Emergency shutdown - allow cooling before restart",
        }
        return actions.get(state)
    
    def get_decisions(
        self,
        limit: int = 50,
        decision_type: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get decisions with optional filtering."""
        result = []
        
        for decision in reversed(self.decisions):
            # Apply filters
            if decision_type and decision.decision_type != decision_type:
                continue
            if category and decision.category != category:
                continue
            if severity and decision.severity != severity:
                continue
            
            result.append(decision.to_dict())
            
            if len(result) >= limit:
                break
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get decision statistics."""
        return {
            **self.stats,
            "session_duration_sec": time.time() - self.session_start,
            "decisions_in_memory": len(self.decisions),
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report of all decisions.
        
        Returns:
            Dictionary containing full report data
        """
        now = time.time()
        session_duration = now - self.session_start
        
        # Get recent decisions by type
        recent_state_changes = self.get_decisions(limit=20, decision_type=self.TYPE_STATE_CHANGE)
        recent_dtcs = self.get_decisions(limit=20, decision_type=self.TYPE_DTC_TRIGGER)
        recent_maintenance = self.get_decisions(limit=20, decision_type=self.TYPE_MAINTENANCE)
        recent_ml = self.get_decisions(limit=20, decision_type=self.TYPE_ML_PREDICTION)
        recent_rul = self.get_decisions(limit=10, decision_type=self.TYPE_RUL_ESTIMATE)
        
        # Get critical decisions
        critical_decisions = self.get_decisions(limit=20, severity="CRITICAL")
        high_decisions = self.get_decisions(limit=20, severity="HIGH")
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "generated_timestamp": now,
                "session_start": datetime.fromtimestamp(self.session_start).isoformat(),
                "session_duration_seconds": session_duration,
                "session_duration_display": self._format_duration(session_duration),
                "report_version": "1.0",
            },
            "summary": {
                "total_decisions": self.stats["total_decisions"],
                "state_transitions": self.stats["state_transitions"],
                "dtcs_triggered": self.stats["dtcs_triggered"],
                "faults_detected": self.stats["faults_detected"],
                "ml_predictions": self.stats["ml_predictions"],
            },
            "statistics": {
                "by_type": self.stats["by_type"],
                "by_category": self.stats["by_category"],
                "by_severity": self.stats["by_severity"],
            },
            "critical_events": critical_decisions,
            "high_priority_events": high_decisions,
            "state_transitions": recent_state_changes,
            "diagnostic_codes": recent_dtcs,
            "maintenance_decisions": recent_maintenance,
            "ml_predictions": recent_ml,
            "rul_estimates": recent_rul,
            "all_decisions": self.get_decisions(limit=100),
        }
        
        return report
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        elif seconds < 3600:
            mins = seconds / 60
            return f"{mins:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.2f} hours"
    
    def clear(self):
        """Clear all decisions and reset stats."""
        self.decisions.clear()
        self.decision_counter = 0
        self.session_start = time.time()
        self.stats = {
            "total_decisions": 0,
            "by_type": {},
            "by_category": {},
            "by_severity": {},
            "state_transitions": 0,
            "dtcs_triggered": 0,
            "faults_detected": 0,
            "ml_predictions": 0,
        }


# Global instance
_tracker: Optional[DecisionTracker] = None


def get_decision_tracker() -> DecisionTracker:
    """Get the global decision tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = DecisionTracker()
    return _tracker
