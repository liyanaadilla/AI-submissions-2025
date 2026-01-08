"""
KPI Evaluation Module for Smart Waste Management System

This module tracks and evaluates key performance indicators:
- Overflow count (bins reaching 100%)
- Total distance traveled
- SLA compliance rate
- Route recomputation time
- Comparison with baseline strategy

AI Component: Performance measurement and explainability
This satisfies FR-15 and FR-16 from the SRS.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import time


@dataclass
class KPISnapshot:
    """
    Snapshot of KPIs at a point in time.
    
    Attributes:
        timestamp: Simulation time step
        overflow_count: Cumulative overflow incidents
        distance_traveled: Total distance by all trucks
        collections_made: Number of bins collected
        sla_violations: Number of SLA breaches
        recomputation_time_ms: Route computation time
        mode: 'AI' or 'Baseline'
    """
    timestamp: int
    overflow_count: int
    distance_traveled: float
    collections_made: int
    sla_violations: int
    recomputation_time_ms: float
    mode: str


@dataclass
class ComparisonResult:
    """
    Result of comparing AI vs Baseline performance.
    
    Attributes:
        ai_kpis: KPIs from AI mode
        baseline_kpis: KPIs from baseline mode
        improvements: Dictionary of improvement percentages
        summary: Human-readable comparison summary
    """
    ai_kpis: KPISnapshot
    baseline_kpis: KPISnapshot
    improvements: Dict[str, float]
    summary: str


class KPITracker:
    """
    Tracks and evaluates system KPIs over time.
    
    AI Component: Quantitative evaluation of AI decisions
    """
    
    def __init__(self, sla_threshold_minutes: float = 120.0):
        """
        Initialize KPI tracker.
        
        Args:
            sla_threshold_minutes: SLA threshold for collection time
        """
        self.sla_threshold = sla_threshold_minutes
        self.snapshots: List[KPISnapshot] = []
        self.current_mode = "AI"
        
        # Cumulative counters
        self.overflow_count = 0
        self.total_distance = 0.0
        self.collections_made = 0
        self.sla_violations = 0
        self.total_recomputation_time = 0.0
        self.recomputation_count = 0
    
    def reset(self) -> None:
        """Reset all KPIs for a new run."""
        self.snapshots = []
        self.overflow_count = 0
        self.total_distance = 0.0
        self.collections_made = 0
        self.sla_violations = 0
        self.total_recomputation_time = 0.0
        self.recomputation_count = 0
    
    def set_mode(self, mode: str) -> None:
        """Set current operation mode (AI or Baseline)."""
        self.current_mode = mode
    
    def record_overflow(self, count: int = 1) -> None:
        """Record overflow incidents."""
        self.overflow_count += count
    
    def record_distance(self, distance: float) -> None:
        """Record distance traveled."""
        self.total_distance += distance
    
    def record_collection(self, eta_at_collection: float) -> None:
        """
        Record a collection event.
        
        Args:
            eta_at_collection: ETA when collection was made (for SLA check)
        """
        self.collections_made += 1
        
        # Check SLA violation (should have been collected earlier)
        if eta_at_collection <= 0:
            self.sla_violations += 1
    
    def record_recomputation(self, time_ms: float) -> None:
        """Record route recomputation time."""
        self.total_recomputation_time += time_ms
        self.recomputation_count += 1
    
    def take_snapshot(self, timestamp: int) -> KPISnapshot:
        """
        Take a snapshot of current KPIs.
        
        Args:
            timestamp: Current simulation time step
        
        Returns:
            KPISnapshot of current state
        """
        avg_recomp_time = (
            self.total_recomputation_time / self.recomputation_count
            if self.recomputation_count > 0 else 0.0
        )
        
        snapshot = KPISnapshot(
            timestamp=timestamp,
            overflow_count=self.overflow_count,
            distance_traveled=round(self.total_distance, 1),
            collections_made=self.collections_made,
            sla_violations=self.sla_violations,
            recomputation_time_ms=round(avg_recomp_time, 2),
            mode=self.current_mode
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_current_kpis(self) -> Dict:
        """
        Get current KPI values as dictionary.
        
        Returns:
            Dictionary of current KPI values
        """
        avg_recomp_time = (
            self.total_recomputation_time / self.recomputation_count
            if self.recomputation_count > 0 else 0.0
        )
        
        sla_compliance = (
            (self.collections_made - self.sla_violations) / self.collections_made * 100
            if self.collections_made > 0 else 100.0
        )
        
        return {
            'overflow_count': self.overflow_count,
            'total_distance': round(self.total_distance, 1),
            'collections_made': self.collections_made,
            'sla_violations': self.sla_violations,
            'sla_compliance_rate': round(sla_compliance, 1),
            'avg_recomputation_time_ms': round(avg_recomp_time, 2),
            'mode': self.current_mode
        }
    
    def get_sla_compliance_rate(self) -> float:
        """
        Calculate SLA compliance rate.
        
        Returns:
            Percentage of collections made within SLA (0-100)
        """
        if self.collections_made == 0:
            return 100.0
        
        compliant = self.collections_made - self.sla_violations
        return (compliant / self.collections_made) * 100


def compare_modes(ai_tracker: KPITracker, 
                  baseline_tracker: KPITracker) -> ComparisonResult:
    """
    Compare AI mode performance against baseline.
    
    AI Component: Demonstrating AI value through quantitative comparison
    
    Args:
        ai_tracker: KPITracker from AI mode run
        baseline_tracker: KPITracker from baseline mode run
    
    Returns:
        ComparisonResult with detailed comparison
    """
    ai_kpis = ai_tracker.get_current_kpis()
    baseline_kpis = baseline_tracker.get_current_kpis()
    
    # Calculate improvements (positive = AI is better)
    improvements = {}
    
    # Overflow reduction (fewer is better)
    if baseline_kpis['overflow_count'] > 0:
        overflow_reduction = (
            (baseline_kpis['overflow_count'] - ai_kpis['overflow_count']) /
            baseline_kpis['overflow_count'] * 100
        )
        improvements['overflow_reduction'] = round(overflow_reduction, 1)
    else:
        improvements['overflow_reduction'] = 0.0
    
    # Distance reduction (less is better)
    if baseline_kpis['total_distance'] > 0:
        distance_reduction = (
            (baseline_kpis['total_distance'] - ai_kpis['total_distance']) /
            baseline_kpis['total_distance'] * 100
        )
        improvements['distance_reduction'] = round(distance_reduction, 1)
    else:
        improvements['distance_reduction'] = 0.0
    
    # SLA improvement
    sla_improvement = ai_kpis['sla_compliance_rate'] - baseline_kpis['sla_compliance_rate']
    improvements['sla_improvement'] = round(sla_improvement, 1)
    
    # Generate summary
    summary_parts = []
    
    if improvements['overflow_reduction'] > 0:
        summary_parts.append(f"🗑️ Reduced overflows by {improvements['overflow_reduction']}%")
    elif improvements['overflow_reduction'] < 0:
        summary_parts.append(f"⚠️ Increased overflows by {-improvements['overflow_reduction']}%")
    
    if improvements['distance_reduction'] > 0:
        summary_parts.append(f"🚚 Reduced distance by {improvements['distance_reduction']}%")
    elif improvements['distance_reduction'] < 0:
        summary_parts.append(f"📍 Increased distance by {-improvements['distance_reduction']}%")
    
    if improvements['sla_improvement'] > 0:
        summary_parts.append(f"✅ Improved SLA compliance by {improvements['sla_improvement']}%")
    elif improvements['sla_improvement'] < 0:
        summary_parts.append(f"⏰ Reduced SLA compliance by {-improvements['sla_improvement']}%")
    
    summary = " | ".join(summary_parts) if summary_parts else "Performance comparable"
    
    # Create snapshot objects for the result
    ai_snapshot = KPISnapshot(
        timestamp=0,
        overflow_count=ai_kpis['overflow_count'],
        distance_traveled=ai_kpis['total_distance'],
        collections_made=ai_kpis['collections_made'],
        sla_violations=ai_kpis['sla_violations'],
        recomputation_time_ms=ai_kpis['avg_recomputation_time_ms'],
        mode='AI'
    )
    
    baseline_snapshot = KPISnapshot(
        timestamp=0,
        overflow_count=baseline_kpis['overflow_count'],
        distance_traveled=baseline_kpis['total_distance'],
        collections_made=baseline_kpis['collections_made'],
        sla_violations=baseline_kpis['sla_violations'],
        recomputation_time_ms=baseline_kpis['avg_recomputation_time_ms'],
        mode='Baseline'
    )
    
    return ComparisonResult(
        ai_kpis=ai_snapshot,
        baseline_kpis=baseline_snapshot,
        improvements=improvements,
        summary=summary
    )


def format_kpi_for_display(kpis: Dict) -> List[Dict]:
    """
    Format KPIs for display in a table.
    
    Args:
        kpis: Dictionary of KPI values
    
    Returns:
        List of dictionaries for table display
    """
    return [
        {'Metric': 'Overflow Incidents', 'Value': kpis['overflow_count'], 'Unit': 'count'},
        {'Metric': 'Total Distance', 'Value': kpis['total_distance'], 'Unit': 'units'},
        {'Metric': 'Collections Made', 'Value': kpis['collections_made'], 'Unit': 'count'},
        {'Metric': 'SLA Compliance', 'Value': f"{kpis['sla_compliance_rate']}%", 'Unit': '%'},
        {'Metric': 'Avg Recomputation Time', 'Value': kpis['avg_recomputation_time_ms'], 'Unit': 'ms'}
    ]
