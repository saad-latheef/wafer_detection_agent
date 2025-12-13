from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool, FunctionTool
from agents.ml_agent import ml_agent


def orchestrate_detection(context):
    """
    Detection orchestration: Coordinates the ML inference process.
    """
    print("\n" + "─"*50)
    print("🔍 [Detection Agent] Orchestrating defect detection")
    print("─"*50)
    
    print("   📋 Current context state:")
    print(f"      - Image path: {context.image_path}")
    print(f"      - Metadata: {context.metadata}")
    
    print("\n   🤔 Decision: I need to run ML inference to detect defects.")
    print("   📤 Delegating to ML Agent...")
    
    # The ML agent will be called through the agent's tools
    return context


detection_agent = Agent(
    name="detection_agent",
    model="gemini-2.5-pro",
    description="Core detection agent that orchestrates the ML pipeline.",
    instruction="""
    You are the Detection Agent.
    Your role is to:
    1. Receive preprocessed image data from the ingestion agent
    2. Delegate to the ML Agent for inference
    3. Ensure probability distribution is computed
    4. Pass results to the analysis agent
    
    Explain your orchestration decisions.
    """,
    tools=[
        FunctionTool(orchestrate_detection),
        AgentTool(ml_agent)
    ],
    output_key="detection_output"
)
