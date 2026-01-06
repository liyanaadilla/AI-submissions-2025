"""
Scheduler Module

Min-heap based task scheduling system for managing deferred tasks.
"""

import heapq
from typing import Dict, List, Any, Optional


class Scheduler:
    """
    Task scheduler using a min-heap priority queue.
    
    Tasks are ordered by due_time and retrieved in chronological order.
    Suitable for: persistence checks, data logging, email alerts.
    """
    
    def __init__(self):
        """Initialize the Scheduler with an empty task queue."""
        self._heap: List[tuple] = []
        self._task_counter = 0  # Counter for stable sorting when due times are equal
    
    def add_task(
        self,
        task_id: str,
        due_time_unix: float,
        payload: Dict[str, Any]
    ) -> None:
        """
        Add a task to the scheduler.
        
        Args:
            task_id: Unique identifier for the task (string)
            due_time_unix: Time when task should be executed (unix timestamp)
            payload: Task data (arbitrary dict)
        """
        # Use counter to ensure stable ordering for tasks with same due_time
        self._task_counter += 1
        heapq.heappush(
            self._heap,
            (due_time_unix, self._task_counter, task_id, payload)
        )
    
    def pop_due_tasks(self, current_time_unix: float) -> List[Dict[str, Any]]:
        """
        Retrieve all tasks that are due at or before the current time.
        
        Tasks are returned in chronological order and removed from the queue.
        
        Args:
            current_time_unix: Current time (unix timestamp)
        
        Returns:
            List of due tasks (each task is {task_id, payload, due_time})
        """
        due_tasks = []
        
        while self._heap:
            # Peek at the top task
            due_time, counter, task_id, payload = self._heap[0]
            
            if due_time <= current_time_unix:
                # Task is due; pop it
                heapq.heappop(self._heap)
                due_tasks.append({
                    "task_id": task_id,
                    "payload": payload,
                    "due_time": due_time,
                })
            else:
                # Task is not due; stop processing
                break
        
        return due_tasks
    
    def clear(self) -> None:
        """Clear all tasks from the scheduler."""
        self._heap = []
        self._task_counter = 0
    
    def pending_count(self) -> int:
        """
        Get count of pending (not yet due) tasks.
        
        Returns:
            Number of tasks in the queue
        """
        return len(self._heap)
    
    def get_next_due_time(self) -> Optional[float]:
        """
        Get the due time of the next task without removing it.
        
        Returns:
            Unix timestamp of next task, or None if queue is empty
        """
        if self._heap:
            return self._heap[0][0]
        return None
    
    def get_debug_state(self) -> Dict[str, Any]:
        """
        Get scheduler state for debugging.
        
        Returns:
            Dictionary with scheduler information
        """
        return {
            "pending_count": len(self._heap),
            "next_due_time": self.get_next_due_time(),
            "task_counter": self._task_counter,
        }
