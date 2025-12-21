"""
Statistical Process Control (SPC) utilities for wafer defect analysis.
Implements Western Electric Rules for control chart analysis.
"""
import statistics
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def calculate_control_limits(data: List[float], sigma: float = 3.0) -> Dict[str, float]:
    """
    Calculate control limits for a dataset.
    
    Args:
        data: List of measurements (e.g., defect rates)
        sigma: Number of standard deviations for control limits (default: 3)
    
    Returns:
        Dictionary with UCL, LCL, CL (center line), and statistics
    """
    if len(data) < 2:
        return {
            "ucl": 100.0,
            "lcl": 0.0,
            "cl": 50.0,
            "std_dev": 0.0,
            "data_points": len(data)
        }
    
    mean = statistics.mean(data)
    std_dev = statistics.stdev(data)
    
    ucl = mean + (sigma * std_dev)
    lcl = max(0, mean - (sigma * std_dev))  # LCL can't be negative for defect rates
    
    return {
        "ucl": round(ucl, 2),
        "lcl": round(lcl, 2),
        "cl": round(mean, 2),
        "std_dev": round(std_dev, 2),
        "data_points": len(data)
    }


def apply_western_electric_rules(
    data: List[Dict[str, Any]], 
    control_limits: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Apply Western Electric Rules to detect out-of-control conditions.
    
    Rules:
    1. One point beyond 3σ
    2. Two of three consecutive points beyond 2σ (same side)
    3. Four of five consecutive points beyond 1σ (same side)
    4. Eight consecutive points on same side of center line
    
    Args:
        data: List of data points with 'value' key
        control_limits: UCL, LCL, CL values
    
    Returns:
        Data with violation flags added
    """
    ucl = control_limits["ucl"]
    lcl = control_limits["lcl"]
    cl = control_limits["cl"]
    std_dev = control_limits["std_dev"]
    
    # Calculate zone boundaries
    zone_a_upper = cl + (2 * std_dev)  # 2σ
    zone_a_lower = cl - (2 * std_dev)
    zone_b_upper = cl + (1 * std_dev)  # 1σ
    zone_b_lower = cl - (1 * std_dev)
    
    results = []
    values = [d.get("value", 0) for d in data]
    
    for i, point in enumerate(data):
        value = point.get("value", 0)
        violations = []
        
        # Rule 1: Beyond 3σ
        if value > ucl or value < lcl:
            violations.append({
                "rule": 1,
                "description": "Point beyond control limits (3σ)",
                "severity": "critical"
            })
        
        # Rule 2: Two of three beyond 2σ (same side)
        if i >= 2:
            recent_3 = values[i-2:i+1]
            above_2sigma = sum(1 for v in recent_3 if v > zone_a_upper)
            below_2sigma = sum(1 for v in recent_3 if v < zone_a_lower)
            if above_2sigma >= 2 or below_2sigma >= 2:
                violations.append({
                    "rule": 2,
                    "description": "2 of 3 points beyond 2σ",
                    "severity": "high"
                })
        
        # Rule 3: Four of five beyond 1σ (same side)
        if i >= 4:
            recent_5 = values[i-4:i+1]
            above_1sigma = sum(1 for v in recent_5 if v > zone_b_upper)
            below_1sigma = sum(1 for v in recent_5 if v < zone_b_lower)
            if above_1sigma >= 4 or below_1sigma >= 4:
                violations.append({
                    "rule": 3,
                    "description": "4 of 5 points beyond 1σ",
                    "severity": "medium"
                })
        
        # Rule 4: Eight consecutive same side
        if i >= 7:
            recent_8 = values[i-7:i+1]
            all_above = all(v > cl for v in recent_8)
            all_below = all(v < cl for v in recent_8)
            if all_above or all_below:
                violations.append({
                    "rule": 4,
                    "description": "8 consecutive points on same side",
                    "severity": "medium"
                })
        
        result = {
            **point,
            "violations": violations,
            "is_out_of_control": len(violations) > 0,
            "zone": _get_zone(value, ucl, lcl, zone_a_upper, zone_a_lower, zone_b_upper, zone_b_lower)
        }
        results.append(result)
    
    return results


def _get_zone(value: float, ucl: float, lcl: float, 
              zone_a_upper: float, zone_a_lower: float,
              zone_b_upper: float, zone_b_lower: float) -> str:
    """Determine which zone a value falls into."""
    if value > ucl or value < lcl:
        return "out_of_control"
    elif value > zone_a_upper or value < zone_a_lower:
        return "zone_a"  # 2-3σ
    elif value > zone_b_upper or value < zone_b_lower:
        return "zone_b"  # 1-2σ
    else:
        return "zone_c"  # Within 1σ


def generate_spc_summary(analyzed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a summary of SPC analysis results.
    """
    total_points = len(analyzed_data)
    violations = [d for d in analyzed_data if d.get("is_out_of_control")]
    
    rule_counts = {}
    for point in violations:
        for v in point.get("violations", []):
            rule = v.get("rule")
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
    
    return {
        "total_points": total_points,
        "out_of_control_count": len(violations),
        "out_of_control_rate": round(len(violations) / total_points * 100, 2) if total_points > 0 else 0,
        "rule_violations": rule_counts,
        "process_stability": "stable" if len(violations) == 0 else 
                           "warning" if len(violations) < 3 else "unstable"
    }
