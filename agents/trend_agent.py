from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool

def analyze_trend(context):
    """
    Trend Analysis tool: Analyzes defect distribution to identify systematic issues.
    """
    print("\n" + "─"*50)
    print("📈 [Trend Agent] Analyzing lot-level defect distribution")
    print("─"*50)
    
    # Get distribution from context
    distribution = context.defect_distribution if hasattr(context, 'defect_distribution') else {}
    
    print(f"   📊 Distribution: {distribution}")
    
    if not distribution:
        context.trend_analysis = "No defect data available for analysis."
        return context

    analysis_lines = []
    
    # Calculate basics
    total_defects = sum(distribution.values())
    sorted_defects = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
    
    if total_defects == 0:
        context.trend_analysis = "✅ No defects detected in this lot. Process is stable."
        return context

    dominant_pattern, count = sorted_defects[0]
    dominance_ratio = count / total_defects
    
    # Generate analysis based on patterns
    if dominance_ratio > 0.5:
        analysis_lines.append(f"⚠️ SYSTEMATIC ISSUE DETECTED: '{dominant_pattern}'")
        analysis_lines.append(f"   This pattern accounts for {dominance_ratio*100:.0f}% of all defects.")
        
        if dominant_pattern == "Loc":
            analysis_lines.append("\n🏭 Root Cause Analysis:")
            analysis_lines.append("   - Likely localized contamination in the deposition chamber.")
            analysis_lines.append("   - Possible particle source directly above the wafer chuck.")
            analysis_lines.append("\n🛠️ Priority Actions:")
            analysis_lines.append("   1. Inspect deposition chamber #3 walls for flaking.")
            analysis_lines.append("   2. Check gas nozzle alignment.")
            
        elif dominant_pattern == "Edge-Ring":
            analysis_lines.append("\n🏭 Root Cause Analysis:")
            analysis_lines.append("   - Issue with Edge Bead Removal (EBR) process.")
            analysis_lines.append("   - Potential spin coater acceleration variance.")
            analysis_lines.append("\n🛠️ Priority Actions:")
            analysis_lines.append("   1. Calibrate EBR nozzle position.")
            analysis_lines.append("   2. Verify spin-coat recipe step 2 (acceleration).")
            
        elif dominant_pattern == "Scratch":
            analysis_lines.append("\n🏭 Root Cause Analysis:")
            analysis_lines.append("   - Mechanical handling error.")
            analysis_lines.append("   - Robotic arm end-effector likely damaged.")
            analysis_lines.append("\n🛠️ Priority Actions:")
            analysis_lines.append("   1. STOP robot #4 for immediate inspection.")
            analysis_lines.append("   2. Check cassette slots for alignment issues.")
            
        elif dominant_pattern == "Donut":
            analysis_lines.append("\n🏭 Root Cause Analysis:")
            analysis_lines.append("   - Thermal gradient issue during bake process.")
            analysis_lines.append("   - Cooling plate non-uniformity.")
            analysis_lines.append("\n🛠️ Priority Actions:")
            analysis_lines.append("   1. Check heater zones 1 & 2 on Bake Plate B.")
            analysis_lines.append("   2. Verify cooling water flow rate.")
            
        elif dominant_pattern == "Edge-Loc":
            analysis_lines.append("\n🏭 Root Cause Analysis:")
            analysis_lines.append("   - Wafer handling machinery gripping too hard.")
            analysis_lines.append("   - Edge exclusion zone violation.")
            analysis_lines.append("\n🛠️ Priority Actions:")
            analysis_lines.append("   1. Adjust aligner grip pressure.")
            analysis_lines.append("   2. Clean edge ring support pins.")
    
    else:
        analysis_lines.append("⚠️ MULTIPLE DEFECT PATTERNS DETECTED")
        analysis_lines.append(f"   No single dominant cause. Top issues: {sorted_defects[0][0]}, {sorted_defects[1][0] if len(sorted_defects)>1 else ''}")
        analysis_lines.append("\n🏭 Root Cause Analysis:")
        analysis_lines.append("   - Likely a general environment or multiple-tool drift.")
        analysis_lines.append("   - Possible cleanroom particle count spike.")
        analysis_lines.append("\n🛠️ Priority Actions:")
        analysis_lines.append("   - Review daily particle counts.")
        analysis_lines.append("   - Check Preventive Maintenance (PM) schedules.")

    result = "\n".join(analysis_lines)
    context.trend_analysis = result
    
    print("\n   📄 Generated Trend Analysis:")
    print("   " + "─"*45)
    print(f"   {result}")
    print("   " + "─"*45)
    
    return context

trend_agent = Agent(
    name="trend_agent",
    model="gemini-2.5-pro",
    description="Analyzes defect distributions to identify systematic root causes.",
    instruction="""
    You are the Trend Analysis Agent.
    Your job is to look at the statistical distribution of wafer defects in a lot.
    If a certain defect type appears frequently, you must identify the systematic process failure causing it.
    Provide specific, technical recommendations for machinery or process steps to check.
    """,
    tools=[FunctionTool(analyze_trend)],
    output_key="trend_output"
)
