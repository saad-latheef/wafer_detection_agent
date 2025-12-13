from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool


def analyze_results(context):
    """
    Analysis tool: Analyzes the probability distribution and image to identify issues.
    Checks for consistency and identifies major problem areas.
    """
    print("\n" + "─"*50)
    print("📊 [Analysis Agent] Analyzing detection results")
    print("─"*50)
    
    prob_dist = context.probability_distribution if hasattr(context, 'probability_distribution') else {}
    predicted_class = context.predicted_class if hasattr(context, 'predicted_class') else "unknown"
    confidence = context.confidence if hasattr(context, 'confidence') else 0.0
    
    print("   🔬 Examining probability distribution...")
    print(f"   📌 Predicted class: {predicted_class}")
    print(f"   📌 Confidence: {confidence*100:.1f}%")
    
    # Identify major issues (classes with significant probability)
    major_issues = []
    print("\n   🔍 Scanning for significant defect probabilities...")
    
    for cls, prob in prob_dist.items():
        if cls != "none" and prob > 0.1:  # Threshold for "significant"
            major_issues.append({"class": cls, "probability": prob})
            print(f"      ⚠️ {cls}: {prob*100:.1f}% - SIGNIFICANT")
        elif prob > 0.05:
            print(f"      📎 {cls}: {prob*100:.1f}% - Minor")
    
    context.major_issues = sorted(major_issues, key=lambda x: x["probability"], reverse=True)
    
    # Consistency check
    print("\n   🧪 Running consistency checks...")
    
    consistency_score = 1.0
    issues_found = []
    
    # Check 1: Is confidence high enough?
    if confidence < 0.3:
        print("      ⚠️ LOW CONFIDENCE: Model is uncertain about prediction")
        consistency_score -= 0.3
        issues_found.append("low_confidence")
    elif confidence < 0.5:
        print("      ⚠️ MODERATE CONFIDENCE: Model has some uncertainty")
        consistency_score -= 0.1
    else:
        print("      ✅ Confidence level acceptable")
    
    # Check 2: Are there competing predictions?
    if len(major_issues) > 2:
        print("      ⚠️ MULTIPLE ISSUES: Several defect types detected")
        consistency_score -= 0.2
        issues_found.append("multiple_defects")
    else:
        print("      ✅ Prediction focus is clear")
    
    # Check 3: Does the prediction make sense?
    if predicted_class == "none" and len(major_issues) > 0:
        print("      ⚠️ INCONSISTENCY: Predicted 'none' but defects detected")
        consistency_score -= 0.3
        issues_found.append("prediction_mismatch")
    else:
        print("      ✅ Prediction is consistent with distribution")
    
    # Determine severity
    if context.has_defect:
        if confidence > 0.8:
            severity = "High"
        elif confidence > 0.5:
            severity = "Medium"
        else:
            severity = "Low"
    else:
        severity = "None"
    
    context.severity = severity
    
    # Build analysis result
    context.analysis_result = {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "major_issues": context.major_issues,
        "consistency_score": consistency_score,
        "issues_found": issues_found,
        "severity": severity,
        "recommendation": "PASS" if consistency_score > 0.6 else "NEEDS_REVIEW"
    }
    
    print("\n   📋 Analysis Summary:")
    print(f"      - Severity: {severity}")
    print(f"      - Consistency Score: {consistency_score:.2f}")
    print(f"      - Issues Found: {issues_found if issues_found else 'None'}")
    print(f"      - Recommendation: {context.analysis_result['recommendation']}")
    
    return context


analysis_agent = Agent(
    name="analysis_agent",
    model="gemini-2.5-pro",
    description="Analyzes the probability distribution and image to validate detection results.",
    instruction="""
    You are the Analysis Agent.
    Your role is to:
    1. Examine the probability distribution from ML inference
    2. Identify major issues and their probabilities
    3. Check for consistency in the results
    4. Determine severity of detected issues
    5. Make a recommendation for validation
    
    Be thorough in your analysis and explain each finding.
    """,
    tools=[FunctionTool(analyze_results)],
    output_key="analysis_output"
)
