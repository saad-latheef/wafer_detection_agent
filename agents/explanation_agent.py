from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool


def generate_explanation(context):
    """
    Explanation tool: Generates a comprehensive human-readable explanation.
    Uses probability distribution, image info, and analysis to form final opinion.
    """
    print("\n" + "─"*50)
    print("📝 [Explanation Agent] Generating comprehensive explanation")
    print("─"*50)
    
    # Gather all information
    image_path = context.image_path if hasattr(context, 'image_path') else "Unknown"
    predicted_class = context.predicted_class if hasattr(context, 'predicted_class') else "Unknown"
    confidence = context.confidence if hasattr(context, 'confidence') else 0.0
    has_defect = context.has_defect if hasattr(context, 'has_defect') else False
    severity = context.severity if hasattr(context, 'severity') else "Unknown"
    major_issues = context.major_issues if hasattr(context, 'major_issues') else []
    analysis = context.analysis_result if hasattr(context, 'analysis_result') else {}
    prob_dist = context.probability_distribution if hasattr(context, 'probability_distribution') else {}
    
    print("   🔍 Reviewing all available information...")
    print(f"      - Image: {image_path}")
    print(f"      - Has defect: {has_defect}")
    print(f"      - Predicted class: {predicted_class}")
    print(f"      - Confidence: {confidence*100:.1f}%")
    print(f"      - Severity: {severity}")
    
    # Build explanation
    explanation_parts = []
    
    # Opening statement
    if has_defect:
        explanation_parts.append(f"⚠️ DEFECT DETECTED on wafer from '{image_path}'")
        explanation_parts.append(f"\n🔍 Primary Defect Type: {predicted_class}")
        explanation_parts.append(f"📊 Confidence Level: {confidence*100:.1f}%")
        explanation_parts.append(f"🚨 Severity Assessment: {severity}")
    else:
        explanation_parts.append(f"✅ NO DEFECTS DETECTED on wafer from '{image_path}'")
        explanation_parts.append(f"📊 Confidence Level: {confidence*100:.1f}%")
    
    # Detailed findings
    if major_issues:
        explanation_parts.append("\n📋 Detailed Findings:")
        for i, issue in enumerate(major_issues, 1):
            explanation_parts.append(f"   {i}. {issue['class']}: {issue['probability']*100:.1f}% probability")
    
    # Analysis insights
    if analysis:
        consistency = analysis.get("consistency_score", 0)
        explanation_parts.append(f"\n🧪 Analysis Quality: {consistency*100:.0f}% consistency")
        
        if analysis.get("issues_found"):
            explanation_parts.append("⚠️ Notes:")
            for issue in analysis["issues_found"]:
                if issue == "low_confidence":
                    explanation_parts.append("   - Model showed uncertainty in prediction")
                elif issue == "multiple_defects":
                    explanation_parts.append("   - Multiple defect types may be present")
                elif issue == "prediction_mismatch":
                    explanation_parts.append("   - Some inconsistency detected in results")
    
    # Probability breakdown
    if prob_dist and has_defect:
        explanation_parts.append("\n📊 Full Probability Breakdown:")
        sorted_probs = sorted(prob_dist.items(), key=lambda x: x[1], reverse=True)
        for cls, prob in sorted_probs[:5]:  # Top 5
            bar = "█" * int(prob * 15)
            explanation_parts.append(f"   {cls:12s}: {prob*100:5.1f}% {bar}")
    
    # Final recommendation
    explanation_parts.append("\n" + "─"*40)
    if has_defect:
        if severity == "High":
            explanation_parts.append("🚨 RECOMMENDATION: IMMEDIATE ACTION REQUIRED")
            explanation_parts.append("   This wafer should be flagged for manual inspection.")
        elif severity == "Medium":
            explanation_parts.append("⚠️ RECOMMENDATION: REVIEW NEEDED")
            explanation_parts.append("   This wafer should be marked for quality review.")
        else:
            explanation_parts.append("📝 RECOMMENDATION: LOG FOR MONITORING")
            explanation_parts.append("   Minor issue detected - log for trend analysis.")
    else:
        explanation_parts.append("✅ RECOMMENDATION: WAFER APPROVED")
        explanation_parts.append("   No defects detected - wafer passes inspection.")
    
    # Compile full explanation
    full_explanation = "\n".join(explanation_parts)
    context.explanation = full_explanation
    
    print("\n   📄 Generated Explanation:")
    print("   " + "─"*45)
    for line in explanation_parts:
        print(f"   {line}")
    print("   " + "─"*45)
    
    return context


explanation_agent = Agent(
    name="explanation_agent",
    model="gemini-2.5-pro",
    description="Generates comprehensive human-readable explanations of detection results.",
    instruction="""
    You are the Explanation Agent.
    Your role is to:
    1. Review all available information (probabilities, analysis, image)
    2. Synthesize a clear, comprehensive explanation
    3. Highlight key findings and their significance
    4. Provide actionable recommendations
    5. Make the explanation accessible to engineers
    
    Be thorough but concise in your explanations.
    """,
    tools=[FunctionTool(generate_explanation)],
    output_key="explanation_output"
)
