from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool


def execute_trigger(context):
    """
    Trigger tool: Executes appropriate actions based on detection results.
    Sends alerts to engineers if defects are found.
    """
    print("\n" + "─"*50)
    print("🚨 [Trigger Agent] Evaluating if action is needed")
    print("─"*50)
    
    has_defect = context.has_defect if hasattr(context, 'has_defect') else False
    severity = context.severity if hasattr(context, 'severity') else "None"
    predicted_class = context.predicted_class if hasattr(context, 'predicted_class') else "Unknown"
    confidence = context.confidence if hasattr(context, 'confidence') else 0.0
    explanation = context.explanation if hasattr(context, 'explanation') else ""
    
    print(f"   📋 Status Check:")
    print(f"      - Defect Found: {has_defect}")
    print(f"      - Severity: {severity}")
    print(f"      - Defect Type: {predicted_class}")
    
    if has_defect:
        print("\n   ⚠️ DEFECT DETECTED - Triggering alert protocol...")
        print("   " + "═"*45)
        
        # Construct alert message
        alert_message = f"""
╔══════════════════════════════════════════════════════════════╗
║                    🚨 WAFER DEFECT ALERT 🚨                   ║
╠══════════════════════════════════════════════════════════════╣
║  Defect Type:    {predicted_class:<42} ║
║  Confidence:     {confidence*100:.1f}%{' '*(40-len(f'{confidence*100:.1f}%'))} ║
║  Severity:       {severity:<42} ║
╠══════════════════════════════════════════════════════════════╣
║  ACTION REQUIRED:                                            ║"""
        
        if severity == "High":
            alert_message += """
║  ► STOP production line for inspection                       ║
║  ► Flag wafer for immediate review                           ║
║  ► Notify Quality Control team                               ║"""
        elif severity == "Medium":
            alert_message += """
║  ► Mark wafer for quality review                             ║
║  ► Continue production with monitoring                       ║
║  ► Log for trend analysis                                    ║"""
        else:
            alert_message += """
║  ► Log defect for monitoring                                 ║
║  ► Continue normal operation                                 ║
║  ► Review in next batch analysis                             ║"""
        
        alert_message += """
╚══════════════════════════════════════════════════════════════╝"""
        
        print(alert_message)
        
        # Simulate sending to engineer
        print("\n   📧 ALERT SENT TO ENGINEER")
        print("   ─────────────────────────────────")
        print("   To: quality-control@semiconductor.com")
        print("   Subject: [ALERT] Wafer Defect Detected")
        print(f"   Body: {predicted_class} defect with {severity} severity")
        print("   ─────────────────────────────────")
        
    else:
        print("\n   ✅ No defects detected - No alerts needed")
        print("   📝 Logging result for records...")
        print("   " + "─"*45)
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    ✅ WAFER INSPECTION PASSED                 ║
╠══════════════════════════════════════════════════════════════╣
║  Status:         APPROVED                                    ║
║  Confidence:     {confidence*100:.1f}%{' '*(40-len(f'{confidence*100:.1f}%'))} ║
║  Action:         Continue to next stage                      ║
╚══════════════════════════════════════════════════════════════╝""")
    
    print("\n   ✅ Trigger agent completed execution")
    
    return context


trigger_agent = Agent(
    name="trigger_agent",
    model="gemini-2.5-pro",
    description="Executes appropriate actions and sends alerts based on detection results.",
    instruction="""
    You are the Trigger Agent.
    Your role is to:
    1. Evaluate if a defect was detected
    2. Determine appropriate action based on severity
    3. Send alerts to engineers if needed
    4. Log results for record keeping
    5. Print clear, actionable messages
    
    Be decisive and clear in your actions.
    """,
    tools=[FunctionTool(execute_trigger)],
    output_key="trigger_output"
)
