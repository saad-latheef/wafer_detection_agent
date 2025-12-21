"""
Data-driven Root Cause Analysis utilities.
Analyzes existing wafer data to identify issues and generate CAPA.
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta


def analyze_defect_data(db_session) -> Dict[str, Any]:
    """
    Analyze wafer data from database to identify top issues and generate CAPA.
    
    Returns comprehensive analysis with:
    - Top defect patterns
    - Problematic tools
    - Trend analysis
    - 5-Why for top issue
    - Fishbone diagram
    - Corrective actions
    - Preventive actions
    """
    from backend.models import Wafer
    from sqlalchemy import func, case
    
    # Get data from last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Query: Defect distribution by pattern
    defect_distribution = db_session.query(
        Wafer.predicted_class,
        func.count(Wafer.id).label('count')
    ).filter(
        Wafer.analyzed_at >= start_date,
        Wafer.final_verdict == 'FAIL'
    ).group_by(Wafer.predicted_class).order_by(func.count(Wafer.id).desc()).all()
    
    # Query: Defects by tool
    tool_defects = db_session.query(
        Wafer.tool_id,
        func.count(Wafer.id).label('total'),
        func.sum(case((Wafer.final_verdict == 'FAIL', 1), else_=0)).label('defective')
    ).filter(
        Wafer.analyzed_at >= start_date
    ).group_by(Wafer.tool_id).all()
    
    # Format tool analysis
    tool_analysis = []
    worst_tool = None
    worst_defect_rate = 0
    
    for tool in tool_defects:
        defect_rate = (tool.defective / tool.total * 100) if tool.total > 0 else 0
        tool_analysis.append({
            "tool_id": tool.tool_id,
            "total_wafers": tool.total,
            "defective": tool.defective,
            "defect_rate": round(defect_rate, 2)
        })
        if defect_rate > worst_defect_rate:
            worst_defect_rate = defect_rate
            worst_tool = tool.tool_id
    
    # Sort by defect rate
    tool_analysis.sort(key=lambda x: x["defect_rate"], reverse=True)
    
    # Format defect distribution
    total_defects = sum(d.count for d in defect_distribution)
    defect_summary = []
    top_defect = None
    
    for d in defect_distribution:
        if d.predicted_class and d.predicted_class != "None":
            percentage = (d.count / total_defects * 100) if total_defects > 0 else 0
            defect_summary.append({
                "pattern": d.predicted_class,
                "count": d.count,
                "percentage": round(percentage, 1)
            })
            if top_defect is None:
                top_defect = d.predicted_class
    
    # Query: Weekly trend for top defect
    weekly_trend = []
    for week_offset in range(4):
        week_end = end_date - timedelta(weeks=week_offset)
        week_start = week_end - timedelta(weeks=1)
        
        count = db_session.query(func.count(Wafer.id)).filter(
            Wafer.analyzed_at >= week_start,
            Wafer.analyzed_at < week_end,
            Wafer.predicted_class == top_defect,
            Wafer.final_verdict == 'FAIL'
        ).scalar() or 0
        
        weekly_trend.append({
            "week": f"Week {4 - week_offset}",
            "count": count
        })
    
    weekly_trend.reverse()
    
    # Determine trend direction
    if len(weekly_trend) >= 2:
        recent = weekly_trend[-1]["count"]
        previous = weekly_trend[-2]["count"]
        trend_direction = "increasing" if recent > previous else "decreasing" if recent < previous else "stable"
    else:
        trend_direction = "insufficient_data"
    
    # Generate 5-Why analysis based on actual data
    five_whys = generate_data_driven_five_whys(top_defect, worst_tool, worst_defect_rate)
    
    # Generate Fishbone based on actual data
    fishbone = generate_data_driven_fishbone(top_defect, worst_tool)
    
    # Generate CAPA (Corrective and Preventive Actions)
    corrective_actions = generate_corrective_actions(top_defect, worst_tool, defect_summary)
    preventive_actions = generate_preventive_actions(top_defect, worst_tool)
    
    return {
        "analysis_date": datetime.now().isoformat(),
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "summary": {
            "total_defects": total_defects,
            "top_defect_pattern": top_defect,
            "worst_tool": worst_tool,
            "worst_tool_defect_rate": round(worst_defect_rate, 2),
            "trend_direction": trend_direction
        },
        "defect_distribution": defect_summary,
        "tool_analysis": tool_analysis,
        "weekly_trend": weekly_trend,
        "five_whys": five_whys,
        "fishbone": fishbone,
        "corrective_actions": corrective_actions,
        "preventive_actions": preventive_actions
    }


def generate_data_driven_five_whys(top_defect: str, worst_tool: str, defect_rate: float) -> List[Dict]:
    """Generate 5-Why analysis based on actual data patterns."""
    
    if not top_defect:
        return []
    
    # Pattern-specific 5-Why chains
    why_chains = {
        "Scratch": [
            {"level": 1, "question": f"Why are we seeing high Scratch defect rates ({defect_rate:.1f}%)?", 
             "answer": f"Data shows {worst_tool} has significantly higher scratch incidence than other tools."},
            {"level": 2, "question": f"Why is {worst_tool} producing more scratches?", 
             "answer": "Wafer handling mechanism likely has worn components or misalignment."},
            {"level": 3, "question": "Why hasn't this wear been detected?", 
             "answer": "Preventive maintenance schedule may not include regular inspection of handling components."},
            {"level": 4, "question": "Why isn't this part of the PM schedule?", 
             "answer": "PM checklist was created before this failure mode was identified as critical."},
            {"level": 5, "question": "What is the root cause?", 
             "answer": "Lack of data-driven PM scheduling that adapts based on actual defect patterns."}
        ],
        "Edge-Ring": [
            {"level": 1, "question": f"Why are Edge-Ring defects at {defect_rate:.1f}%?", 
             "answer": f"{worst_tool} shows concentration of edge defects, suggesting chamber edge effects."},
            {"level": 2, "question": f"Why does {worst_tool} have chamber edge issues?", 
             "answer": "Edge bead removal (EBR) process may be incomplete or EBR nozzle is clogged."},
            {"level": 3, "question": "Why isn't EBR effectiveness being monitored?", 
             "answer": "No automated metrology for edge uniformity after EBR step."},
            {"level": 4, "question": "Why no automated monitoring?", 
             "answer": "Investment in edge-specific metrology was deprioritized."},
            {"level": 5, "question": "What is the root cause?", 
             "answer": "Insufficient process monitoring at wafer edges combined with aging EBR equipment."}
        ],
        "Center": [
            {"level": 1, "question": f"Why are Center defects concentrated on {worst_tool}?", 
             "answer": "Chuck vacuum or thermal uniformity issues at wafer center."},
            {"level": 2, "question": "Why is thermal uniformity affected?", 
             "answer": "Chuck heater may have degraded zones or vacuum leaks at center."},
            {"level": 3, "question": "Why wasn't this caught during qualification?", 
             "answer": "Qualification uses limited wafer sample, may miss gradual degradation."},
            {"level": 4, "question": "Why no continuous monitoring?", 
             "answer": "Temperature sensors only at chuck periphery, not center."},
            {"level": 5, "question": "What is the root cause?", 
             "answer": "Insufficient sensor coverage for chuck thermal uniformity monitoring."}
        ]
    }
    
    # Return specific chain or generic
    return why_chains.get(top_defect, [
        {"level": 1, "question": f"Why are {top_defect} defects elevated?", 
         "answer": f"Analysis shows {worst_tool} is the primary contributor with {defect_rate:.1f}% defect rate."},
        {"level": 2, "question": "Why is this tool underperforming?", 
         "answer": "Equipment degradation or process drift over time."},
        {"level": 3, "question": "Why wasn't drift detected earlier?", 
         "answer": "SPC alerts may not have been configured for this specific pattern."},
        {"level": 4, "question": "Why no pattern-specific monitoring?", 
         "answer": "Monitoring focused on overall yield, not defect-type breakdown."},
        {"level": 5, "question": "What is the root cause?", 
         "answer": "Need for more granular defect pattern tracking and tool-specific alerting."}
    ])


def generate_data_driven_fishbone(top_defect: str, worst_tool: str) -> Dict[str, List[str]]:
    """Generate Fishbone categories based on actual data patterns."""
    
    base_fishbone = {
        "man": [
            f"Operator training on {worst_tool} handling procedures",
            "Shift handoff communication gaps",
            "Recipe selection errors"
        ],
        "machine": [
            f"{worst_tool} requires maintenance inspection",
            "Sensor calibration due for review",
            "Component wear based on usage hours"
        ],
        "material": [
            "Incoming wafer quality variation",
            "Photoresist batch consistency",
            "Chemical lot changes"
        ],
        "method": [
            "Recipe parameter optimization needed",
            "Process step sequence review",
            f"SPC alerts for {top_defect} pattern"
        ],
        "measurement": [
            "Metrology sampling frequency",
            "Defect detection sensitivity",
            "Measurement recipe accuracy"
        ],
        "environment": [
            "Cleanroom particle counts",
            "Temperature/humidity stability",
            "AMC (airborne molecular contamination)"
        ]
    }
    
    return base_fishbone


def generate_corrective_actions(top_defect: str, worst_tool: str, defect_summary: List) -> List[Dict]:
    """Generate immediate corrective actions based on data."""
    
    actions = [
        {
            "priority": "Critical",
            "action": f"Perform immediate maintenance inspection on {worst_tool}",
            "owner": "Equipment Engineering",
            "due": "24 hours",
            "rationale": f"Data shows {worst_tool} has highest defect contribution"
        },
        {
            "priority": "High", 
            "action": f"Run qualification wafers on {worst_tool} after maintenance",
            "owner": "Process Engineering",
            "due": "48 hours",
            "rationale": "Verify equipment performance before resuming production"
        },
        {
            "priority": "High",
            "action": f"Review recent {top_defect} defects for common characteristics",
            "owner": "Defect Engineering",
            "due": "48 hours",
            "rationale": f"{top_defect} is the dominant defect pattern"
        },
        {
            "priority": "Medium",
            "action": "Audit wafer handling procedures across all shifts",
            "owner": "Manufacturing",
            "due": "1 week",
            "rationale": "Rule out human factors as contributing cause"
        }
    ]
    
    return actions


def generate_preventive_actions(top_defect: str, worst_tool: str) -> List[Dict]:
    """Generate long-term preventive actions based on data."""
    
    actions = [
        {
            "priority": "High",
            "action": f"Add {top_defect}-specific SPC monitoring with automated alerts",
            "owner": "Yield Engineering",
            "due": "2 weeks",
            "expected_impact": "Early detection of pattern recurrence"
        },
        {
            "priority": "High",
            "action": f"Update PM schedule for {worst_tool} based on defect correlation",
            "owner": "Equipment Engineering", 
            "due": "2 weeks",
            "expected_impact": "Prevent equipment-related defects"
        },
        {
            "priority": "Medium",
            "action": "Implement tool-specific defect dashboards",
            "owner": "IT/Analytics",
            "due": "1 month",
            "expected_impact": "Faster identification of tool issues"
        },
        {
            "priority": "Medium",
            "action": "Create defect pattern training module for operators",
            "owner": "Training",
            "due": "1 month",
            "expected_impact": "Improved defect recognition and escalation"
        },
        {
            "priority": "Low",
            "action": "Evaluate predictive maintenance solutions",
            "owner": "Equipment Engineering",
            "due": "3 months",
            "expected_impact": "Proactive equipment issue prevention"
        }
    ]
    
    return actions
