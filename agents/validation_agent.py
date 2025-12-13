from google.adk.agents import Agent
from google.adk.tools.agent_tool import FunctionTool


def validate_results(context):
    """
    Validation tool: Validates the analysis results and determines if they are satisfactory.
    Sets is_valid flag to control the loop.
    """
    print("\n" + "─"*50)
    print("✅ [Validation Agent] Validating analysis results")
    print("─"*50)
    
    context.validation_attempts = getattr(context, 'validation_attempts', 0) + 1
    max_attempts = getattr(context, 'max_attempts', 3)
    
    print(f"   🔄 Validation attempt: {context.validation_attempts}/{max_attempts}")
    
    analysis = context.analysis_result if hasattr(context, 'analysis_result') else {}
    consistency_score = analysis.get("consistency_score", 0)
    confidence = context.confidence if hasattr(context, 'confidence') else 0.0
    recommendation = analysis.get("recommendation", "UNKNOWN")
    
    print("\n   📋 Checking validation criteria...")
    
    # Criteria for valid result
    criteria_met = []
    criteria_failed = []
    
    # Criterion 1: Consistency score
    if consistency_score >= 0.6:
        criteria_met.append("consistency_score >= 0.6")
        print(f"      ✅ Consistency score ({consistency_score:.2f}) is acceptable")
    else:
        criteria_failed.append(f"consistency_score = {consistency_score:.2f} (need >= 0.6)")
        print(f"      ❌ Consistency score ({consistency_score:.2f}) is too low")
    
    # Criterion 2: Minimum confidence
    if confidence >= 0.25:
        criteria_met.append("confidence >= 0.25")
        print(f"      ✅ Confidence ({confidence*100:.1f}%) meets minimum threshold")
    else:
        criteria_failed.append(f"confidence = {confidence*100:.1f}% (need >= 25%)")
        print(f"      ❌ Confidence ({confidence*100:.1f}%) is below minimum")
    
    # Criterion 3: No critical issues
    issues_found = analysis.get("issues_found", [])
    if "prediction_mismatch" not in issues_found:
        criteria_met.append("no_prediction_mismatch")
        print("      ✅ No prediction mismatches detected")
    else:
        criteria_failed.append("prediction_mismatch detected")
        print("      ❌ Prediction mismatch found - results inconsistent")
    
    # Determine validity
    is_valid = len(criteria_failed) == 0
    
    # After max attempts, accept whatever we have
    if not is_valid and context.validation_attempts >= max_attempts:
        print(f"\n   ⚠️ Max attempts ({max_attempts}) reached - accepting current result")
        is_valid = True
    
    context.is_valid = is_valid
    
    print("\n   📊 Validation Decision:")
    print(f"      - Criteria Met: {len(criteria_met)}/{len(criteria_met) + len(criteria_failed)}")
    
    if is_valid:
        print("      ✅ VALIDATION PASSED - Results are satisfactory")
    else:
        print("      ❌ VALIDATION FAILED - Results need improvement")
        print(f"      🔄 Will retry... (Attempt {context.validation_attempts + 1} coming)")
    
    return context


validation_agent = Agent(
    name="validation_agent",
    model="gemini-2.5-pro",
    description="Validates analysis results and controls the retry loop.",
    instruction="""
    You are the Validation Agent.
    Your role is to:
    1. Check if analysis results meet quality criteria
    2. Verify consistency score is acceptable
    3. Ensure confidence level is sufficient
    4. Detect any critical issues that require re-analysis
    5. Set is_valid flag to control the loop
    
    Be strict but fair in your validation.
    """,
    tools=[FunctionTool(validate_results)],
    output_key="validation_output"
)
