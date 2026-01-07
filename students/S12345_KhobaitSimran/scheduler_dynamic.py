"""
Dynamic Maintenance Scheduler Module

Priority-based task scheduling with dynamic reordering based on:
- Fault severity
- Asset criticality  
- Remaining Useful Life (RUL)

Priority Formula: P_s = (W_severity × C_asset) / RUL
"""

import heapq
import time
from typing import Dict, List, Any, Optional
from enum import Enum


class TaskSeverity(Enum):
    """Task severity weights per YSMAI_Project_Planning.txt"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 5
    EMERGENCY = 10


class AssetCriticality(Enum):
    """Asset criticality coefficients"""
    AUXILIARY = 0.5       # Non-critical systems
    STANDARD = 1.0        # Normal operations
    IMPORTANT = 1.5       # Important but not critical
    CRITICAL = 2.0        # Critical systems
    SAFETY_CRITICAL = 3.0 # Safety-related systems


class MaintenanceTask:
    """Represents a maintenance task with priority scoring."""
    
    def __init__(
        self,
        task_id: str,
        name: str,
        description: str,
        task_type: str,  # 'oil_change', 'filter', 'inspection', 'repair', etc.
        severity: TaskSeverity = TaskSeverity.MEDIUM,
        asset_criticality: AssetCriticality = AssetCriticality.STANDARD,
        base_due_hours: float = 100.0,  # Default due in 100 hours
        estimated_duration_min: int = 30,
        dtc_codes: List[str] = None,
    ):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.task_type = task_type
        self.severity = severity
        self.asset_criticality = asset_criticality
        self.base_due_hours = base_due_hours
        self.estimated_duration_min = estimated_duration_min
        self.dtc_codes = dtc_codes or []
        
        # Dynamic state
        self.remaining_hours = base_due_hours
        self.priority_score = 0.0
        self.created_at = time.time()
        self.status = "pending"  # pending, in_progress, completed, overdue
    
    def calculate_priority(self, rul_hours: Optional[float] = None) -> float:
        """
        Calculate priority score: P_s = (W_severity × C_asset) / RUL
        
        Higher score = more urgent
        """
        w_severity = self.severity.value
        c_asset = self.asset_criticality.value
        
        # Use remaining hours as RUL if not provided
        rul = rul_hours if rul_hours is not None else self.remaining_hours
        
        # Prevent division by zero, use very high priority for overdue
        if rul <= 0:
            rul = 0.01  # Very small number = very high priority
        
        self.priority_score = (w_severity * c_asset) / rul
        return self.priority_score
    
    def update_remaining_time(self, hours_elapsed: float) -> None:
        """Update remaining hours and status."""
        self.remaining_hours = max(0, self.remaining_hours - hours_elapsed)
        
        if self.remaining_hours <= 0:
            self.status = "overdue"
        elif self.remaining_hours < self.base_due_hours * 0.25:
            self.status = "soon"
        else:
            self.status = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "severity": self.severity.name,
            "asset_criticality": self.asset_criticality.name,
            "remaining_hours": round(self.remaining_hours, 1),
            "due_in_display": self._format_due_time(),
            "priority_score": round(self.priority_score, 3),
            "status": self._get_status_display(),
            "estimated_duration_min": self.estimated_duration_min,
            "dtc_codes": self.dtc_codes,
        }
    
    def _format_due_time(self) -> str:
        """Format remaining time for display."""
        hours = self.remaining_hours
        if hours <= 0:
            return "OVERDUE"
        if hours < 1:
            return f"Due in {int(hours * 60)} min"
        if hours < 24:
            return f"Due in {hours:.1f} hours"
        days = hours / 24
        return f"Due in {days:.1f} days"
    
    def _get_status_display(self) -> str:
        """Get status for UI display."""
        if self.status == "overdue":
            return "Overdue"
        if self.remaining_hours < self.base_due_hours * 0.25:
            return "Soon"
        return "OK"


class DynamicScheduler:
    """
    Dynamic maintenance scheduler with priority-based ordering.
    
    Features:
    - Priority queue using min-heap (negated for max-priority first)
    - Dynamic reprioritization based on sensor data
    - DTC-triggered task injection
    - RUL-aware scheduling
    """
    
    # DTC to task mapping for automatic task injection
    DTC_TASK_MAP = {
        "P0217": ("emergency_cooling_check", "Emergency Cooling System Check", TaskSeverity.EMERGENCY),
        "P0522": ("emergency_oil_check", "Emergency Oil System Check", TaskSeverity.EMERGENCY),
        "P0562": ("battery_check", "Battery/Charging System Check", TaskSeverity.HIGH),
        "P0563": ("voltage_regulator_check", "Voltage Regulator Inspection", TaskSeverity.HIGH),
        "P2263": ("vibration_inspection", "Vibration Source Inspection", TaskSeverity.CRITICAL),
        "P0521": ("oil_pressure_sensor_check", "Oil Pressure Sensor Calibration", TaskSeverity.HIGH),
        "P0118": ("coolant_sensor_check", "Coolant Temperature Sensor Check", TaskSeverity.MEDIUM),
    }
    
    def __init__(self):
        """Initialize the dynamic scheduler."""
        self.tasks: Dict[str, MaintenanceTask] = {}
        self._heap: List[tuple] = []
        self._task_counter = 0
        self.simulation_hours = 0.0
        
        # Initialize with standard maintenance tasks
        self._init_standard_tasks()
    
    def _init_standard_tasks(self) -> None:
        """Initialize standard periodic maintenance tasks."""
        standard_tasks = [
            MaintenanceTask(
                task_id="oil_change_1",
                name="Oil Change",
                description="Replace engine oil and oil filter",
                task_type="oil_change",
                severity=TaskSeverity.HIGH,
                asset_criticality=AssetCriticality.CRITICAL,
                base_due_hours=45.0,
                estimated_duration_min=45,
            ),
            MaintenanceTask(
                task_id="filter_replace_1",
                name="Air Filter Replacement",
                description="Replace primary and secondary air filters",
                task_type="filter",
                severity=TaskSeverity.MEDIUM,
                asset_criticality=AssetCriticality.IMPORTANT,
                base_due_hours=120.0,
                estimated_duration_min=20,
            ),
            MaintenanceTask(
                task_id="valve_inspect_1",
                name="Valve Inspection",
                description="Inspect intake and exhaust valve clearances",
                task_type="inspection",
                severity=TaskSeverity.MEDIUM,
                asset_criticality=AssetCriticality.STANDARD,
                base_due_hours=300.0,
                estimated_duration_min=60,
            ),
            MaintenanceTask(
                task_id="coolant_check_1",
                name="Coolant Level Check",
                description="Check coolant level and condition",
                task_type="inspection",
                severity=TaskSeverity.MEDIUM,
                asset_criticality=AssetCriticality.IMPORTANT,
                base_due_hours=50.0,
                estimated_duration_min=10,
            ),
            MaintenanceTask(
                task_id="belt_inspect_1",
                name="Belt Inspection",
                description="Inspect drive belts for wear and tension",
                task_type="inspection",
                severity=TaskSeverity.LOW,
                asset_criticality=AssetCriticality.STANDARD,
                base_due_hours=200.0,
                estimated_duration_min=15,
            ),
        ]
        
        for task in standard_tasks:
            self.add_task(task)
    
    def add_task(self, task: MaintenanceTask) -> None:
        """Add a task to the scheduler."""
        self.tasks[task.task_id] = task
        self._rebuild_heap()
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the scheduler."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._rebuild_heap()
            return True
        return False
    
    def complete_task(self, task_id: str) -> Optional[MaintenanceTask]:
        """Mark a task as completed and reset its schedule."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.remaining_hours = task.base_due_hours
            task.status = "pending"
            self._rebuild_heap()
            return task
        return None
    
    def update(
        self,
        elapsed_hours: float,
        active_dtcs: List[Dict[str, Any]] = None,
        rul_hours: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Update scheduler with elapsed time and current conditions.
        
        Args:
            elapsed_hours: Hours elapsed since last update
            active_dtcs: List of active DTC codes from agent
            rul_hours: Estimated remaining useful life in hours
            
        Returns:
            Sorted list of tasks by priority
        """
        self.simulation_hours += elapsed_hours
        
        # Update remaining time for all tasks
        for task in self.tasks.values():
            task.update_remaining_time(elapsed_hours)
            task.calculate_priority(rul_hours)
        
        # Inject DTC-triggered tasks
        if active_dtcs:
            for dtc in active_dtcs:
                dtc_code = dtc.get("code", "")
                if dtc_code in self.DTC_TASK_MAP:
                    self._inject_dtc_task(dtc_code)
        
        # Rebuild priority heap
        self._rebuild_heap()
        
        # Return sorted tasks
        return self.get_sorted_tasks()
    
    def _inject_dtc_task(self, dtc_code: str) -> None:
        """Inject an emergency task based on DTC code."""
        if dtc_code not in self.DTC_TASK_MAP:
            return
        
        task_id, name, severity = self.DTC_TASK_MAP[dtc_code]
        
        # Check if task already exists
        if task_id in self.tasks:
            # Escalate severity if needed
            existing = self.tasks[task_id]
            if severity.value > existing.severity.value:
                existing.severity = severity
            existing.remaining_hours = min(existing.remaining_hours, 1.0)  # Due soon
            return
        
        # Create new emergency task
        task = MaintenanceTask(
            task_id=task_id,
            name=name,
            description=f"Triggered by DTC {dtc_code}",
            task_type="emergency",
            severity=severity,
            asset_criticality=AssetCriticality.SAFETY_CRITICAL,
            base_due_hours=1.0,  # Due immediately
            estimated_duration_min=30,
            dtc_codes=[dtc_code],
        )
        self.add_task(task)
    
    def _rebuild_heap(self) -> None:
        """Rebuild the priority heap."""
        self._heap = []
        self._task_counter = 0
        
        for task in self.tasks.values():
            # Negate priority for max-heap behavior (highest priority first)
            self._task_counter += 1
            heapq.heappush(
                self._heap,
                (-task.priority_score, self._task_counter, task.task_id)
            )
    
    def get_sorted_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tasks sorted by priority (highest first)."""
        # Sort by priority score descending
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.priority_score,
            reverse=True
        )
        return [t.to_dict() for t in sorted_tasks[:limit]]
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the highest priority task."""
        if not self._heap:
            return None
        
        _, _, task_id = self._heap[0]
        return self.tasks[task_id].to_dict() if task_id in self.tasks else None
    
    def get_overdue_count(self) -> int:
        """Get count of overdue tasks."""
        return sum(1 for t in self.tasks.values() if t.status == "overdue")
    
    def get_soon_count(self) -> int:
        """Get count of tasks due soon."""
        return sum(1 for t in self.tasks.values() if t.status == "soon")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "total_tasks": len(self.tasks),
            "overdue_count": self.get_overdue_count(),
            "soon_count": self.get_soon_count(),
            "simulation_hours": round(self.simulation_hours, 2),
        }
    
    def clear(self) -> None:
        """Clear all tasks and reinitialize."""
        self.tasks = {}
        self._heap = []
        self._task_counter = 0
        self.simulation_hours = 0.0
        self._init_standard_tasks()
