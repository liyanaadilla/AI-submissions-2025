"""
AI Agent Core Engine - PEAS Model Implementation
Implements Sense-Reason-Act cycle for industrial automation
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import random

# Type definitions
TaskStatus = str  # "pending" | "in-progress" | "completed"
TaskPriority = str  # "low" | "medium" | "high"
WorkerStatus = str  # "available" | "busy"
MachineStatus = str  # "normal" | "warning" | "critical"
AlertType = str  # "maintenance" | "anomaly" | "system"
AlertSeverity = str  # "low" | "medium" | "high"

@dataclass
class Task:
    id: str
    name: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    completed_at: Optional[datetime] = None

@dataclass
class Worker:
    id: str
    name: str
    status: WorkerStatus
    skill_type: str
    current_task: Optional[str] = None

@dataclass
class Machine:
    id: str
    name: str
    temperature: float
    vibration: float
    status: MachineStatus
    last_maintenance: Optional[datetime] = None

@dataclass
class Resource:
    id: str
    name: str
    current_usage: float
    optimal_usage: float
    is_optimized: bool

@dataclass
class Alert:
    id: str
    type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool

@dataclass
class ActionLog:
    step: int
    action: str
    details: str
    timestamp: datetime

@dataclass
class SystemState:
    tasks: List[Task]
    workers: List[Worker]
    machines: List[Machine]
    resources: List[Resource]
    alerts: List[Alert]
    action_history: List[ActionLog]
    current_step: int


class AIEngine:
    """AI Agent implementing PEAS model with Sense-Reason-Act cycle"""
    
    def __init__(self):
        self.reset()
    
    def _generate_initial_state(self) -> SystemState:
        """Generate initial system state"""
        return SystemState(
            tasks=[
                Task(
                    id="task-1", name="Quality Inspection A", status="pending", priority="high"
                ),
                Task(
                    id="task-2", name="Assembly Line Setup", status="pending", priority="medium"
                ),
                Task(
                    id="task-3", name="Packaging Process", status="pending", priority="medium"
                ),
                Task(
                    id="task-4", name="Inventory Check", status="pending", priority="low"
                ),
            ],
            workers=[
                Worker(
                    id="worker-1", name="Robot Arm A", status="available", skill_type="assembly"
                ),
                Worker(
                    id="worker-2", name="Inspector Unit B", status="available", skill_type="inspection"
                ),
                Worker(
                    id="worker-3", name="Packaging Bot C", status="available", skill_type="packaging"
                ),
            ],
            machines=[
                Machine(
                    id="machine-1", name="CNC Machine 01", temperature=55.0, vibration=0.7, status="normal"
                ),
                Machine(
                    id="machine-2", name="Press Unit 02", temperature=62.0, vibration=0.8, status="normal"
                ),
                Machine(
                    id="machine-3", name="Conveyor System 03", temperature=48.0, vibration=0.5, status="normal"
                ),
            ],
            resources=[
                Resource(
                    id="resource-1", name="Power Consumption", current_usage=85.0, optimal_usage=75.0, is_optimized=False
                ),
                Resource(
                    id="resource-2", name="Material Flow", current_usage=92.0, optimal_usage=80.0, is_optimized=False
                ),
                Resource(
                    id="resource-3", name="Network Bandwidth", current_usage=68.0, optimal_usage=70.0, is_optimized=True
                ),
            ],
            alerts=[],
            action_history=[],
            current_step=0
        )
    
    def sense(self) -> SystemState:
        """SENSE: Read current system state"""
        return self.state
    
    def reason(self) -> Optional[str]:
        """REASON: Evaluate conditions and decide on actions"""
        
        # Priority 1: Check for critical machine conditions
        critical_machine = next((m for m in self.state.machines if m.status == "critical"), None)
        if critical_machine:
            return f"schedule-maintenance:{critical_machine.id}"
        
        # Priority 2: Check for warning conditions
        warning_machine = next((m for m in self.state.machines if m.status == "warning"), None)
        if warning_machine:
            return f"alert-maintenance:{warning_machine.id}"
        
        # Priority 3: Complete in-progress tasks
        in_progress_task = next((t for t in self.state.tasks if t.status == "in-progress"), None)
        if in_progress_task and random.random() > 0.3:
            return f"complete-task:{in_progress_task.id}"
        
        # Priority 4: Assign high priority pending tasks
        high_priority_task = next((t for t in self.state.tasks if t.status == "pending" and t.priority == "high"), None)
        if high_priority_task:
            available_worker = next((w for w in self.state.workers if w.status == "available"), None)
            if available_worker:
                return f"assign-task:{high_priority_task.id}:{available_worker.id}"
        
        # Priority 5: Check for unoptimized resources
        unoptimized_resource = next((r for r in self.state.resources if not r.is_optimized), None)
        if unoptimized_resource:
            return f"optimize-resource:{unoptimized_resource.id}"
        
        # Priority 6: Assign medium priority tasks
        medium_priority_task = next((t for t in self.state.tasks if t.status == "pending" and t.priority == "medium"), None)
        if medium_priority_task:
            available_worker = next((w for w in self.state.workers if w.status == "available"), None)
            if available_worker:
                return f"assign-task:{medium_priority_task.id}:{available_worker.id}"
        
        # Priority 7: Assign low priority tasks
        low_priority_task = next((t for t in self.state.tasks if t.status == "pending" and t.priority == "low"), None)
        if low_priority_task:
            available_worker = next((w for w in self.state.workers if w.status == "available"), None)
            if available_worker:
                return f"assign-task:{low_priority_task.id}:{available_worker.id}"
        
        # Priority 8: Detect anomalies occasionally
        if random.random() > 0.7:
            random_machine = random.choice(self.state.machines)
            return f"detect-anomaly:{random_machine.id}"
        
        return "confirm-normal"
    
    def act(self, action: str) -> SystemState:
        """ACT: Execute the decided action"""
        parts = action.split(":")
        action_type = parts[0]
        params = parts[1:] if len(parts) > 1 else []
        
        if action_type == "assign-task" and len(params) >= 2:
            task_id, worker_id = params[0], params[1]
            task = next((t for t in self.state.tasks if t.id == task_id), None)
            worker = next((w for w in self.state.workers if w.id == worker_id), None)
            
            if task and worker and task.status == "pending" and worker.status == "available":
                task.status = "in-progress"
                task.assigned_to = worker.id  # Store worker ID, not name
                worker.status = "busy"
                worker.current_task = task_id
                self._log_action(f"Assigned '{task.name}' to '{worker.name}'")
        
        elif action_type == "complete-task" and len(params) >= 1:
            task_id = params[0]
            task = next((t for t in self.state.tasks if t.id == task_id), None)
            
            if task and task.status == "in-progress":
                task.status = "completed"
                task.completed_at = datetime.now()
                
                # Find and free the worker
                if task.assigned_to:
                    worker = next((w for w in self.state.workers if w.id == task.assigned_to), None)
                    if worker:
                        worker.status = "available"
                        worker.current_task = None
                
                self._log_action(f"Completed '{task.name}'")
        
        elif action_type == "schedule-maintenance" and len(params) >= 1:
            machine_id = params[0]
            machine = next((m for m in self.state.machines if m.id == machine_id), None)
            
            if machine:
                machine.status = "normal"
                machine.temperature = 45 + random.random() * 10
                machine.vibration = 0.5 + random.random() * 0.3
                machine.last_maintenance = datetime.now()
                
                # Remove related alerts
                self.state.alerts = [a for a in self.state.alerts if machine.name not in a.message]
                
                self._log_action(f"Scheduled maintenance for '{machine.name}'")
        
        elif action_type == "alert-maintenance" and len(params) >= 1:
            machine_id = params[0]
            machine = next((m for m in self.state.machines if m.id == machine_id), None)
            
            if machine:
                existing_alert = next((a for a in self.state.alerts if machine.name in a.message and not a.resolved), None)
                
                if not existing_alert:
                    self.state.alerts.append(Alert(
                        id=f"alert-{int(datetime.now().timestamp())}",
                        type="maintenance",
                        severity="medium",
                        message=f"{machine.name} requires maintenance check",
                        timestamp=datetime.now(),
                        resolved=False
                    ))
                    
                    self._log_action(f"Created maintenance alert for '{machine.name}'")
        
        elif action_type == "optimize-resource" and len(params) >= 1:
            resource_id = params[0]
            resource = next((r for r in self.state.resources if r.id == resource_id), None)
            
            if resource:
                resource.current_usage = resource.optimal_usage
                resource.is_optimized = True
                self._log_action(f"Optimized '{resource.name}' usage")
        
        elif action_type == "detect-anomaly" and len(params) >= 1:
            machine_id = params[0]
            machine = next((m for m in self.state.machines if m.id == machine_id), None)
            
            if machine:
                machine.temperature += 15 + random.random() * 10
                machine.vibration += 0.5 + random.random() * 0.5
                
                if machine.temperature > 85:
                    machine.status = "critical"
                elif machine.temperature > 70:
                    machine.status = "warning"
                
                self.state.alerts.append(Alert(
                    id=f"alert-{int(datetime.now().timestamp())}",
                    type="anomaly",
                    severity="high" if machine.status == "critical" else "medium",
                    message=f"Anomaly detected in {machine.name}",
                    timestamp=datetime.now(),
                    resolved=False
                ))
                
                self._log_action(f"Detected anomaly in '{machine.name}'")
        
        elif action_type == "confirm-normal":
            self._log_action("System state confirmed normal")
        
        return self.state
    
    def _log_action(self, details: str):
        """Log an action to the history"""
        self.state.action_history.append(ActionLog(
            step=self.state.current_step + 1,
            action=details,
            details=details,
            timestamp=datetime.now()
        ))
    
    def execute_step(self) -> Dict[str, Any]:
        """Main AI Loop: Sense → Reason → Act"""
        print(f"\n=== Executing Step {self.state.current_step + 1} ===")
        
        self.sense()
        decision = self.reason()
        
        print(f"AI Decision: {decision}")
        
        if decision:
            self.act(decision)
        
        # Update machine status based on temperature/vibration
        for machine in self.state.machines:
            if machine.temperature > 85:
                machine.status = "critical"
            elif machine.temperature > 70:
                machine.status = "warning"
            else:
                machine.status = "normal"
        
        # Always try to assign a pending task if workers are available
        pending_tasks = [t for t in self.state.tasks if t.status == "pending"]
        available_workers = [w for w in self.state.workers if w.status == "available"]
        
        if pending_tasks and available_workers and random.random() > 0.4:
            task = pending_tasks[0]
            worker = available_workers[0]
            print(f"Assigning task '{task.name}' to worker '{worker.name}'")
            self.act(f"assign-task:{task.id}:{worker.id}")
        
        # Randomly complete some in-progress tasks
        for task in self.state.tasks:
            if task.status == "in-progress" and random.random() > 0.5:
                print(f"Completing task: {task.name}")
                self.act(f"complete-task:{task.id}")
        
        # Increment step
        self.state.current_step += 1
        
        print(f"Step {self.state.current_step} completed")
        
        return self.get_state_dict()
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get current state as dictionary"""
        return {
            'tasks': [asdict(t) for t in self.state.tasks],
            'workers': [asdict(w) for w in self.state.workers],
            'machines': [asdict(m) for m in self.state.machines],
            'resources': [asdict(r) for r in self.state.resources],
            'alerts': [asdict(a) for a in self.state.alerts],
            'action_history': [asdict(a) for a in self.state.action_history],
            'current_step': self.state.current_step
        }
    
    def calculate_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics"""
        completed_tasks = [t for t in self.state.tasks if t.status == "completed"]
        total_tasks = len(self.state.tasks)
        
        # Calculate actual completion time based on completed tasks
        if completed_tasks:
            avg_time = sum((datetime.now() - t.completed_at).seconds for t in completed_tasks if t.completed_at) / len(completed_tasks) / 60
        else:
            avg_time = 3.5
        
        return {
            'avg_task_completion_time': avg_time,
            'error_reduction_rate': (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0,
            'downtime_avoided': len([m for m in self.state.machines if m.status == "normal"]) * 25,
            'resource_efficiency': (len([r for r in self.state.resources if r.is_optimized]) / len(self.state.resources) * 100) if len(self.state.resources) > 0 else 0
        }
    
    def calculate_system_overview(self) -> Dict[str, int]:
        """Calculate system overview metrics"""
        active_tasks = len([t for t in self.state.tasks if t.status == "in-progress"])
        available_workers = len([w for w in self.state.workers if w.status == "available"])
        healthy_machines = len([m for m in self.state.machines if m.status == "normal"])
        critical_alerts = len([a for a in self.state.alerts if a.severity == "high" and not a.resolved])
        
        return {
            'active_tasks': active_tasks,
            'available_workers': available_workers,
            'healthy_machines': healthy_machines,
            'critical_alerts': critical_alerts
        }
    
    def reset(self):
        """Reset the system to initial state"""
        self.state = self._generate_initial_state()
