"""
Prediction Module for Smart Waste Management System

This module provides waste level prediction capabilities:
- Estimated Time to Full (ETA) computation
- Trend-based forecasting

AI Component: Predictive analytics for proactive decision-making
Formula: ETA(b) = (1 - fill_level) / fill_rate

This satisfies FR-4 and FR-5 from the SRS.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PredictionResult:
    """
    Result of ETA prediction for a bin.
    
    Attributes:
        bin_id: Bin identifier
        current_fill: Current fill level (0-100%)
        fill_rate: Rate of fill increase per time step
        eta_minutes: Estimated time until full (minutes)
        confidence: Prediction confidence (0-1)
    """
    bin_id: int
    current_fill: float
    fill_rate: float
    eta_minutes: float
    confidence: float = 1.0


def predict_eta(fill_level: float, fill_rate: float, 
                minutes_per_step: float = 30.0) -> float:
    """
    Predict Estimated Time to Full (ETA) for a waste bin.
    
    AI Component: This implements a simple trend-based prediction model.
    The prediction assumes constant fill rate (linear extrapolation).
    
    Formula: ETA = (100 - fill_level) / fill_rate * minutes_per_step
    
    Args:
        fill_level: Current fill percentage (0-100)
        fill_rate: Fill rate per time step (% per step)
        minutes_per_step: Real-time minutes each simulation step represents
    
    Returns:
        Estimated minutes until bin is 100% full
        Returns 0 if already full, float('inf') if fill_rate is 0
    
    Example:
        >>> predict_eta(50.0, 2.0, 30.0)  # 50% full, 2% per step
        750.0  # 25 steps * 30 minutes = 750 minutes
    """
    if fill_level >= 100.0:
        return 0.0
    
    if fill_rate <= 0:
        return float('inf')  # Never fills if rate is zero or negative
    
    remaining_capacity = 100.0 - fill_level
    steps_to_full = remaining_capacity / fill_rate
    
    return steps_to_full * minutes_per_step


def predict_all_bins(bins: Dict, minutes_per_step: float = 30.0) -> List[PredictionResult]:
    """
    Predict ETA for all bins in the system.
    
    Args:
        bins: Dictionary of bin_id -> WasteBin objects
        minutes_per_step: Real-time minutes each simulation step represents
    
    Returns:
        List of PredictionResult objects sorted by ETA (most urgent first)
    """
    predictions = []
    
    for bin_id, bin_obj in bins.items():
        eta = predict_eta(
            fill_level=bin_obj.fill_level,
            fill_rate=bin_obj.fill_rate,
            minutes_per_step=minutes_per_step
        )
        
        # Calculate confidence based on data quality
        # Lower confidence for very low or very high fill rates
        confidence = calculate_confidence(bin_obj.fill_level, bin_obj.fill_rate)
        
        predictions.append(PredictionResult(
            bin_id=bin_id,
            current_fill=bin_obj.fill_level,
            fill_rate=bin_obj.fill_rate,
            eta_minutes=eta,
            confidence=confidence
        ))
    
    # Sort by ETA (most urgent first)
    predictions.sort(key=lambda p: p.eta_minutes)
    
    return predictions


def calculate_confidence(fill_level: float, fill_rate: float) -> float:
    """
    Calculate confidence score for ETA prediction.
    
    Higher confidence when:
    - Fill level is moderate (not too low or high)
    - Fill rate is consistent and reasonable
    
    Args:
        fill_level: Current fill percentage
        fill_rate: Fill rate per time step
    
    Returns:
        Confidence score between 0 and 1
    """
    # Base confidence
    confidence = 1.0
    
    # Lower confidence for extreme fill levels
    if fill_level < 10 or fill_level > 90:
        confidence *= 0.8
    
    # Lower confidence for unusual fill rates
    if fill_rate < 0.1 or fill_rate > 5.0:
        confidence *= 0.7
    
    return round(confidence, 2)


def get_prediction_summary(predictions: List[PredictionResult]) -> Dict:
    """
    Generate summary statistics for predictions.
    
    Args:
        predictions: List of PredictionResult objects
    
    Returns:
        Dictionary with summary statistics
    """
    if not predictions:
        return {
            'count': 0,
            'avg_eta': 0,
            'min_eta': 0,
            'urgent_count': 0,
            'critical_count': 0
        }
    
    etas = [p.eta_minutes for p in predictions if p.eta_minutes != float('inf')]
    
    urgent_count = sum(1 for p in predictions if p.eta_minutes <= 120)  # <= 2 hours
    critical_count = sum(1 for p in predictions if p.eta_minutes <= 60)  # <= 1 hour
    
    return {
        'count': len(predictions),
        'avg_eta': round(sum(etas) / len(etas), 1) if etas else float('inf'),
        'min_eta': round(min(etas), 1) if etas else float('inf'),
        'urgent_count': urgent_count,
        'critical_count': critical_count
    }
