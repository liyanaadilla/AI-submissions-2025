#!/usr/bin/env python3
"""
Session Manager Module for YSMAI

Handles:
- Auto-checkpointing (every N minutes/ticks)
- Session lifecycle (create, checkpoint, archive)
- Multi-session comparison
- Persistent storage (Firebase)
- Session history tracking
"""

import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from uuid import uuid4


@dataclass
class SessionCheckpoint:
    """Represents a snapshot of system state at a checkpoint."""
    checkpoint_id: str
    session_id: str
    timestamp: float
    tick_count: int
    simulation_time: float
    
    # State snapshot
    temperature: float
    state: str
    severity: str
    
    # Statistics at checkpoint
    decision_count: int
    state_changes: int
    dtcs_triggered: int
    faults_detected: int
    
    # Alert status
    active_dtcs: List[str]
    active_alerts_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "timestamp_display": datetime.fromtimestamp(self.timestamp).isoformat(),
        }


@dataclass
class SessionSummary:
    """Summary of a completed session."""
    session_id: str
    timestamp_start: float
    timestamp_end: float
    duration_seconds: float
    tick_count_start: int
    tick_count_end: int
    
    # Session metadata
    checkpoint_count: int
    trigger_reason: str  # "auto", "manual", "critical_event"
    
    # Statistics
    total_decisions: int
    state_transitions: int
    dtcs_triggered: int
    faults_detected: int
    max_severity: str
    
    # Temperature statistics
    temp_min: float
    temp_max: float
    temp_avg: float
    
    # Saved state
    saved_to_db: bool = False
    firebase_document_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "timestamp_start_display": datetime.fromtimestamp(self.timestamp_start).isoformat(),
            "timestamp_end_display": datetime.fromtimestamp(self.timestamp_end).isoformat(),
            "duration_display": self._format_duration(self.duration_seconds),
        }
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.2f}h"


class SessionManager:
    """
    Manages sessions with auto-checkpointing capability.
    
    Features:
    - Auto-checkpoint at regular intervals or on critical events
    - Session history tracking
    - Comparison across sessions
    - Firebase persistence
    - Graceful degradation without Firebase
    """
    
    # Checkpoint trigger types
    TRIGGER_AUTO = "auto"
    TRIGGER_MANUAL = "manual"
    TRIGGER_CRITICAL = "critical_event"
    TRIGGER_STATE_CHANGE = "state_change"
    
    def __init__(
        self,
        checkpoint_interval_ticks: int = 600,  # ~5 minutes at 0.5s/tick
        auto_checkpoint_enabled: bool = True,
    ):
        """
        Initialize session manager.
        
        Args:
            checkpoint_interval_ticks: Ticks between auto-checkpoints
            auto_checkpoint_enabled: Enable automatic checkpointing
        """
        self.checkpoint_interval_ticks = checkpoint_interval_ticks
        self.auto_checkpoint_enabled = auto_checkpoint_enabled
        
        # Current session tracking
        self.current_session_id = self._generate_session_id()
        self.session_start_time = time.time()
        self.session_start_tick = 0
        
        # Checkpoint tracking
        self.last_checkpoint_tick = 0
        self.checkpoints: List[SessionCheckpoint] = []
        
        # Session history
        self.session_history: List[SessionSummary] = []
        
        # Temperature tracking for statistics
        self.temperature_readings: List[float] = []
        
        # Critical event tracking
        self.critical_events_count = 0
        self.max_severity = "INFO"
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        return f"session_{timestamp}_{unique_id}"
    
    def _generate_checkpoint_id(self) -> str:
        """Generate unique checkpoint ID."""
        return f"checkpoint_{uuid4().hex[:12]}"
    
    def should_checkpoint(self, current_tick: int, trigger_event: Optional[str] = None) -> bool:
        """
        Determine if checkpoint should be created.
        
        Args:
            current_tick: Current simulation tick
            trigger_event: Optional event that triggered checkpoint check
                          (e.g., "state_change", "critical_alert")
        
        Returns:
            True if checkpoint should be created
        """
        if not self.auto_checkpoint_enabled and trigger_event is None:
            return False
        
        # Auto-checkpoint at regular intervals
        ticks_since_last = current_tick - self.last_checkpoint_tick
        if ticks_since_last >= self.checkpoint_interval_ticks:
            return True
        
        # Critical events trigger immediate checkpoint
        if trigger_event in ["critical_alert", "fault_detected", "state_change_critical"]:
            return True
        
        return False
    
    def create_checkpoint(
        self,
        current_tick: int,
        simulation_time: float,
        sensor_data: Dict[str, Any],
        decision_stats: Dict[str, Any],
        trigger_reason: str = "auto",
    ) -> SessionCheckpoint:
        """
        Create a session checkpoint (snapshot).
        
        Args:
            current_tick: Current simulation tick
            simulation_time: Simulation time elapsed
            sensor_data: Current sensor data
            decision_stats: Current decision statistics
            trigger_reason: Why checkpoint was created
        
        Returns:
            Created checkpoint object
        """
        checkpoint = SessionCheckpoint(
            checkpoint_id=self._generate_checkpoint_id(),
            session_id=self.current_session_id,
            timestamp=time.time(),
            tick_count=current_tick,
            simulation_time=simulation_time,
            temperature=sensor_data.get("temperature", 0.0),
            state=sensor_data.get("state", "UNKNOWN"),
            severity=sensor_data.get("severity", "INFO"),
            decision_count=decision_stats.get("total_decisions", 0),
            state_changes=decision_stats.get("state_transitions", 0),
            dtcs_triggered=decision_stats.get("dtcs_triggered", 0),
            faults_detected=decision_stats.get("faults_detected", 0),
            active_dtcs=[d.get("code") for d in sensor_data.get("active_dtcs", [])],
            active_alerts_count=len(sensor_data.get("active_dtcs", [])),
        )
        
        self.checkpoints.append(checkpoint)
        self.last_checkpoint_tick = current_tick
        
        return checkpoint
    
    def record_tick_data(
        self,
        tick_count: int,
        temperature: float,
        severity: str,
        decision_stats: Dict[str, Any],
    ):
        """Record data from each tick for session statistics."""
        self.temperature_readings.append(temperature)
        
        if severity == "CRITICAL":
            self.critical_events_count += 1
        
        # Update max severity
        severity_order = {"INFO": 0, "WARNING": 1, "CRITICAL": 2}
        if severity_order.get(severity, 0) > severity_order.get(self.max_severity, 0):
            self.max_severity = severity
    
    def end_session(
        self,
        current_tick: int,
        decision_tracker: Optional[Any] = None,
        trigger_reason: str = "manual",
    ) -> SessionSummary:
        """
        End current session and create summary.
        
        Args:
            current_tick: Final tick count
            decision_tracker: Optional decision tracker for statistics
            trigger_reason: Why session ended
        
        Returns:
            Session summary
        """
        now = time.time()
        duration = now - self.session_start_time
        
        # Get decision statistics
        if decision_tracker:
            stats = decision_tracker.get_stats()
        else:
            stats = {
                "total_decisions": 0,
                "state_transitions": 0,
                "dtcs_triggered": 0,
                "faults_detected": 0,
            }
        
        # Calculate temperature statistics
        if self.temperature_readings:
            temp_min = min(self.temperature_readings)
            temp_max = max(self.temperature_readings)
            temp_avg = sum(self.temperature_readings) / len(self.temperature_readings)
        else:
            temp_min = temp_max = temp_avg = 0.0
        
        summary = SessionSummary(
            session_id=self.current_session_id,
            timestamp_start=self.session_start_time,
            timestamp_end=now,
            duration_seconds=duration,
            tick_count_start=self.session_start_tick,
            tick_count_end=current_tick,
            checkpoint_count=len(self.checkpoints),
            trigger_reason=trigger_reason,
            total_decisions=stats.get("total_decisions", 0),
            state_transitions=stats.get("state_transitions", 0),
            dtcs_triggered=stats.get("dtcs_triggered", 0),
            faults_detected=stats.get("faults_detected", 0),
            max_severity=self.max_severity,
            temp_min=temp_min,
            temp_max=temp_max,
            temp_avg=temp_avg,
            saved_to_db=False,
        )
        
        self.session_history.append(summary)
        return summary
    
    def start_new_session(self, from_tick: int = 0):
        """Start a new session (for next checkpoint cycle)."""
        self.current_session_id = self._generate_session_id()
        self.session_start_time = time.time()
        self.session_start_tick = from_tick
        self.last_checkpoint_tick = from_tick
        self.checkpoints.clear()
        self.temperature_readings.clear()
        self.critical_events_count = 0
        self.max_severity = "INFO"
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        elapsed = time.time() - self.session_start_time
        return {
            "session_id": self.current_session_id,
            "elapsed_seconds": elapsed,
            "checkpoint_count": len(self.checkpoints),
            "temperature_samples": len(self.temperature_readings),
            "critical_events": self.critical_events_count,
            "max_severity": self.max_severity,
            "auto_checkpoint_enabled": self.auto_checkpoint_enabled,
        }
    
    def get_session_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent session summaries."""
        return [s.to_dict() for s in self.session_history[-limit:]]
    
    def get_all_checkpoints(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get checkpoints for a session."""
        if session_id is None:
            session_id = self.current_session_id
        
        checkpoints = [
            cp.to_dict() for cp in self.checkpoints
            if cp.session_id == session_id
        ]
        return checkpoints
    
    def compare_sessions(self, session_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple sessions.
        
        Args:
            session_ids: List of session IDs to compare
        
        Returns:
            Comparison report
        """
        sessions = [
            s for s in self.session_history
            if s.session_id in session_ids
        ]
        
        if not sessions:
            return {"error": "No sessions found"}
        
        # Calculate metrics
        metrics = {
            "count": len(sessions),
            "total_decisions": sum(s.total_decisions for s in sessions),
            "avg_decisions": sum(s.total_decisions for s in sessions) / len(sessions),
            "total_dtcs": sum(s.dtcs_triggered for s in sessions),
            "total_faults": sum(s.faults_detected for s in sessions),
            "avg_duration_sec": sum(s.duration_seconds for s in sessions) / len(sessions),
            "temp_range": {
                "min": min(s.temp_min for s in sessions),
                "max": max(s.temp_max for s in sessions),
                "avg": sum(s.temp_avg * s.duration_seconds for s in sessions) / sum(s.duration_seconds for s in sessions) if sum(s.duration_seconds for s in sessions) > 0 else 0,
            },
            "severity_distribution": {
                "CRITICAL": sum(1 for s in sessions if s.max_severity == "CRITICAL"),
                "WARNING": sum(1 for s in sessions if s.max_severity == "WARNING"),
                "INFO": sum(1 for s in sessions if s.max_severity == "INFO"),
            },
            "sessions": [s.to_dict() for s in sessions],
        }
        
        return metrics


# Global instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create the global session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
