"""
Knowledge-Based Reasoning Module for Smart Waste Management System

This module implements rule-based reasoning for bin classification:
- Full: fill_level >= 80%
- Urgent: ETA <= 120 minutes
- Eligible: (Full OR Urgent) AND not collected
- OverCapacity: Adding bin would exceed truck capacity

AI Component: Knowledge Representation (KR) using production rules
This satisfies FR-6 and FR-7 from the SRS.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from modules.prediction import predict_eta


class BinStatus(Enum):
    """Enumeration of bin status classifications."""
    NORMAL = "Normal"
    FULL = "Full"
    URGENT = "Urgent"
    ELIGIBLE = "Eligible"
    COLLECTED = "Collected"


class ReasoningStatus(Enum):
    """Reasoning-phase classification for bins."""
    GREEN = "green"      # Eligible for service
    ORANGE = "orange"    # Urgent but blocked (capacity / assigned / constraint)
    GREY = "grey"        # Not relevant


@dataclass
class ReasoningResult:
    """
    Result of KR-based reasoning for a bin.
    
    Attributes:
        bin_id: Bin identifier
        status: GREEN, ORANGE, or GREY
        is_predicted: Whether this bin was in the prediction output
        block_reason: Reason for blocking if ORANGE
        explanation: Human-readable explanation
    """
    bin_id: int
    status: ReasoningStatus
    is_predicted: bool
    block_reason: str = ""
    explanation: str = ""


@dataclass
class RuleResult:
    """
    Result of rule-based classification for a bin.
    
    Attributes:
        bin_id: Bin identifier
        is_full: True if fill >= 80%
        is_urgent: True if ETA <= 120 minutes
        is_eligible: True if should be collected
        status: Overall status classification
        explanation: Human-readable explanation of classification
    """
    bin_id: int
    is_full: bool
    is_urgent: bool
    is_eligible: bool
    status: BinStatus
    explanation: str


# ============================================================
# RULE DEFINITIONS (Knowledge Base)
# ============================================================
# These rules encode domain knowledge about waste collection priority

# Thresholds (can be adjusted)
FULL_THRESHOLD = 80.0  # % fill level
URGENT_THRESHOLD = 120.0  # minutes until full


def rule_is_full(fill_level: float, threshold: float = FULL_THRESHOLD) -> bool:
    """
    RULE: Full(b) ← fill_level(b) ≥ 80%
    
    A bin is considered FULL when it has reached or exceeded
    the threshold fill level and requires collection.
    
    Args:
        fill_level: Current fill percentage (0-100)
        threshold: Fill level threshold for "full" status
    
    Returns:
        True if bin is full
    """
    return fill_level >= threshold


def rule_is_urgent(eta_minutes: float, threshold: float = URGENT_THRESHOLD) -> bool:
    """
    RULE: Urgent(b) ← ETA(b) ≤ 120 minutes
    
    A bin is URGENT when it will overflow within the threshold time,
    even if not currently full. Requires proactive collection.
    
    Args:
        eta_minutes: Estimated time to full in minutes
        threshold: Time threshold for "urgent" status
    
    Returns:
        True if bin is urgent
    """
    return eta_minutes <= threshold


def rule_is_eligible(is_full: bool, is_urgent: bool, is_collected: bool) -> bool:
    """
    RULE: Eligible(b) ← (Full(b) ∨ Urgent(b)) ∧ ¬Collected(b)
    
    A bin is ELIGIBLE for collection if it is either full or urgent,
    AND has not already been collected in the current cycle.
    
    Args:
        is_full: Result of Full rule
        is_urgent: Result of Urgent rule
        is_collected: Whether bin has been collected
    
    Returns:
        True if bin is eligible for collection
    """
    return (is_full or is_urgent) and not is_collected


def rule_over_capacity(truck_load: float, truck_capacity: float, 
                       bin_fill: float) -> bool:
    """
    RULE: OverCap(t, b) ← load(t) + fill(b) > capacity(t)
    
    Check if adding a bin's waste would exceed truck capacity.
    Used to filter feasible assignments.
    
    Args:
        truck_load: Current truck load
        truck_capacity: Maximum truck capacity
        bin_fill: Waste amount in the bin
    
    Returns:
        True if adding bin would exceed capacity
    """
    return truck_load + bin_fill > truck_capacity


# ============================================================
# INFERENCE ENGINE
# ============================================================

def classify_bin(bin_obj, minutes_per_step: float = 30.0) -> RuleResult:
    """
    Apply all rules to classify a single bin.
    
    This is the inference engine that chains rules together
    to produce a final classification.
    
    Args:
        bin_obj: WasteBin object to classify
        minutes_per_step: Minutes per simulation step for ETA calculation
    
    Returns:
        RuleResult with classification details
    """
    # Get max capacity (default to 100 for percentage-based systems)
    max_capacity = getattr(bin_obj, 'max_capacity', 100)
    fill_percentage = (bin_obj.fill_level / max_capacity) * 100 if max_capacity > 0 else 0
    
    # Calculate ETA for this bin (using percentage-based fill)
    eta = predict_eta(
        fill_level=fill_percentage,
        fill_rate=bin_obj.fill_rate,
        minutes_per_step=minutes_per_step
    )
    
    # Apply rules (using percentage)
    is_full = rule_is_full(fill_percentage)
    is_urgent = rule_is_urgent(eta)
    is_eligible = rule_is_eligible(is_full, is_urgent, bin_obj.collected)
    
    # Determine overall status
    if bin_obj.collected:
        status = BinStatus.COLLECTED
    elif is_eligible:
        status = BinStatus.ELIGIBLE
    elif is_full:
        status = BinStatus.FULL
    elif is_urgent:
        status = BinStatus.URGENT
    else:
        status = BinStatus.NORMAL
    
    # Generate explanation
    explanation = generate_explanation(
        bin_obj.id, bin_obj.fill_level, eta, 
        is_full, is_urgent, is_eligible, bin_obj.collected
    )
    
    return RuleResult(
        bin_id=bin_obj.id,
        is_full=is_full,
        is_urgent=is_urgent,
        is_eligible=is_eligible,
        status=status,
        explanation=explanation
    )


def classify_all_bins(bins: Dict, minutes_per_step: float = 30.0) -> List[RuleResult]:
    """
    Classify all bins in the system.
    
    Args:
        bins: Dictionary of bin_id -> WasteBin objects
        minutes_per_step: Minutes per simulation step
    
    Returns:
        List of RuleResult objects for all bins
    """
    results = []
    
    for bin_id, bin_obj in bins.items():
        result = classify_bin(bin_obj, minutes_per_step)
        results.append(result)
    
    return results


def get_eligible_bins(bins: Dict, minutes_per_step: float = 30.0) -> List[int]:
    """
    Get list of bin IDs that are eligible for collection.
    
    Args:
        bins: Dictionary of bin_id -> WasteBin objects
        minutes_per_step: Minutes per simulation step
    
    Returns:
        List of eligible bin IDs
    """
    classifications = classify_all_bins(bins, minutes_per_step)
    return [r.bin_id for r in classifications if r.is_eligible]


def filter_by_capacity(eligible_bins: List[int], bins: Dict, 
                       truck_load: float, truck_capacity: float) -> List[int]:
    """
    Filter eligible bins by truck capacity constraint.
    
    Args:
        eligible_bins: List of eligible bin IDs
        bins: Dictionary of bin_id -> WasteBin objects
        truck_load: Current truck load
        truck_capacity: Maximum truck capacity
    
    Returns:
        List of bin IDs that can be collected given capacity
    """
    feasible = []
    
    for bin_id in eligible_bins:
        bin_obj = bins[bin_id]
        if not rule_over_capacity(truck_load, truck_capacity, bin_obj.fill_level):
            feasible.append(bin_id)
    
    return feasible


def generate_explanation(bin_id: int, fill_level: float, eta: float,
                        is_full: bool, is_urgent: bool, 
                        is_eligible: bool, is_collected: bool) -> str:
    """
    Generate human-readable explanation of rule application.
    
    AI Component: Explainability - making AI decisions transparent
    
    Args:
        Various rule inputs and results
    
    Returns:
        Human-readable explanation string
    """
    parts = [f"Bin {bin_id}:"]
    
    # Fill status
    parts.append(f"Fill={fill_level:.1f}%")
    
    # ETA status
    if eta == float('inf'):
        parts.append("ETA=∞")
    elif eta == 0:
        parts.append("ETA=0 (full)")
    else:
        parts.append(f"ETA={eta:.0f}min")
    
    # Rule results
    rules_fired = []
    if is_full:
        rules_fired.append(f"FULL(≥{FULL_THRESHOLD}%)")
    if is_urgent:
        rules_fired.append(f"URGENT(≤{URGENT_THRESHOLD}min)")
    if is_collected:
        rules_fired.append("COLLECTED")
    
    if rules_fired:
        parts.append("→ " + ", ".join(rules_fired))
    
    # Final decision
    if is_eligible:
        parts.append("⇒ ELIGIBLE for collection")
    elif is_collected:
        parts.append("⇒ Already collected")
    else:
        parts.append("⇒ Not priority")
    
    return " | ".join(parts)


def get_reasoning_summary(classifications: List[RuleResult]) -> Dict:
    """
    Summarize reasoning results for display.
    
    Args:
        classifications: List of RuleResult objects
    
    Returns:
        Dictionary with summary statistics
    """
    return {
        'total_bins': len(classifications),
        'full_count': sum(1 for r in classifications if r.is_full),
        'urgent_count': sum(1 for r in classifications if r.is_urgent),
        'eligible_count': sum(1 for r in classifications if r.is_eligible),
        'collected_count': sum(1 for r in classifications if r.status == BinStatus.COLLECTED),
        'normal_count': sum(1 for r in classifications if r.status == BinStatus.NORMAL)
    }


# ============================================================
# REASONING PHASE (KR Filtering)
# ============================================================

def reason_all_bins(
    bins: Dict,
    predicted_bin_ids: List[int],
    trucks: Dict,
    minutes_per_step: float = 30.0
) -> List[ReasoningResult]:
    """
    Apply KR rules to ALL bins, using Predict output as input context.
    
    This is the key reasoning step that filters bins into:
    - GREEN: Eligible for service
    - ORANGE: Urgent but blocked (capacity / assigned / constraint)
    - GREY: Not relevant
    
    Important:
    - Some predicted bins can become ineligible (ORANGE)
    - Some non-predicted bins can still be eligible (e.g., full but stable)
    
    Args:
        bins: Dictionary of all bin_id -> WasteBin objects
        predicted_bin_ids: List of bin IDs from prediction phase (context)
        trucks: Dictionary of truck_id -> Truck objects
        minutes_per_step: Minutes per simulation step
    
    Returns:
        List of ReasoningResult for ALL bins
    """
    results = []
    predicted_set = set(predicted_bin_ids)
    
    # Calculate total available capacity across all trucks
    total_capacity = sum(t.capacity - t.current_load for t in trucks.values())
    
    # Sort bins by priority (fill level + urgency) for capacity allocation
    all_classifications = classify_all_bins(bins, minutes_per_step)
    class_map = {c.bin_id: c for c in all_classifications}
    
    # Track capacity used for blocking logic
    capacity_used = 0
    assigned_count = 0
    max_assignments = len(trucks) * 5  # Max bins per truck (constraint)
    
    for bin_id, bin_obj in bins.items():
        classification = class_map.get(bin_id)
        is_predicted = bin_id in predicted_set
        
        # Calculate fill percentage for rule checks
        max_capacity = getattr(bin_obj, 'max_capacity', 100)
        fill_pct = (bin_obj.fill_level / max_capacity) * 100 if max_capacity > 0 else 0
        
        # Apply KR rules to determine status
        is_full = classification.is_full if classification else rule_is_full(fill_pct)
        is_urgent = classification.is_urgent if classification else False
        is_collected = bin_obj.collected
        
        # Base eligibility check
        base_eligible = rule_is_eligible(is_full, is_urgent, is_collected)
        
        # Determine final status with constraint checking
        if is_collected:
            # Already collected - Grey
            status = ReasoningStatus.GREY
            block_reason = ""
            explanation = f"Bin {bin_id}: Already collected this cycle"
            
        elif not base_eligible:
            # Not full and not urgent - Grey (not relevant)
            status = ReasoningStatus.GREY
            block_reason = ""
            explanation = f"Bin {bin_id}: Fill={fill_pct:.1f}% - Not priority"
            
        else:
            # Base eligible - check constraints
            bin_waste = bin_obj.fill_level
            
            # Constraint 1: Capacity check
            if capacity_used + bin_waste > total_capacity:
                status = ReasoningStatus.ORANGE
                block_reason = "Capacity Constraint"
                explanation = f"Bin {bin_id}: Urgent but BLOCKED - Fleet capacity exceeded"
                
            # Constraint 2: Assignment limit check
            elif assigned_count >= max_assignments:
                status = ReasoningStatus.ORANGE
                block_reason = "Assignment Limit"
                explanation = f"Bin {bin_id}: Urgent but BLOCKED - Max assignments reached"
                
            else:
                # All constraints passed - GREEN
                status = ReasoningStatus.GREEN
                block_reason = ""
                capacity_used += bin_waste
                assigned_count += 1
                
                status_label = "FULL" if is_full else "URGENT"
                source_label = "(predicted)" if is_predicted else "(detected)"
                explanation = f"Bin {bin_id}: {status_label} {source_label} → ELIGIBLE for collection"
        
        results.append(ReasoningResult(
            bin_id=bin_id,
            status=status,
            is_predicted=is_predicted,
            block_reason=block_reason,
            explanation=explanation
        ))
    
    return results


def get_green_bins(reasoning_results: List[ReasoningResult]) -> List[int]:
    """
    Get list of bin IDs that are GREEN (eligible for service).
    
    Args:
        reasoning_results: List of ReasoningResult objects
    
    Returns:
        List of GREEN bin IDs
    """
    return [r.bin_id for r in reasoning_results if r.status == ReasoningStatus.GREEN]


def get_reasoning_phase_summary(reasoning_results: List[ReasoningResult]) -> Dict:
    """
    Summarize reasoning phase results for display.
    
    Args:
        reasoning_results: List of ReasoningResult objects
    
    Returns:
        Dictionary with summary statistics
    """
    return {
        'total_bins': len(reasoning_results),
        'green_count': sum(1 for r in reasoning_results if r.status == ReasoningStatus.GREEN),
        'orange_count': sum(1 for r in reasoning_results if r.status == ReasoningStatus.ORANGE),
        'grey_count': sum(1 for r in reasoning_results if r.status == ReasoningStatus.GREY),
        'from_prediction': sum(1 for r in reasoning_results if r.is_predicted),
        'blocked_reasons': [r.block_reason for r in reasoning_results if r.block_reason]
    }
