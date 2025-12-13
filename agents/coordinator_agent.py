from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.agent_tool import AgentTool

from agents.ingestion_agent import ingestion_agent
from agents.detection_loop_agent import detection_loop_agent
from agents.explanation_agent import explanation_agent
from agents.trigger_agent import trigger_agent


# The Coordinator Agent orchestrates the entire pipeline
# Flow: Ingestion -> Detection Loop -> Explanation -> Trigger

coordinator_agent = Agent(
    name="coordinator_agent",
    model="gemini-2.5-pro",
    description="Root orchestrator for the Wafer Detection System.",
    instruction="""
    You are the Coordinator Agent - the central orchestrator of the Wafer Detection System.
    
    Your workflow is:
    1. First, call the Ingestion Agent to prepare the input image
    2. Then, delegate to the Detection Loop Agent which will:
       - Run detection (ML inference)
       - Analyze results
       - Validate (and retry if needed)
    3. After validation passes, call the Explanation Agent for final report
    4. Finally, call the Trigger Agent to execute appropriate actions
    
    Ensure each step completes before moving to the next.
    """,
    tools=[
        AgentTool(ingestion_agent),
        AgentTool(detection_loop_agent),
        AgentTool(explanation_agent),
        AgentTool(trigger_agent)
    ],
    output_key="final_result"
)

# Alternative: Use SequentialAgent for guaranteed order
coordinator_sequential = SequentialAgent(
    name="coordinator_sequential",
    description="Sequential orchestrator ensuring ordered execution.",
    sub_agents=[
        ingestion_agent,
        detection_loop_agent,
        explanation_agent,
        trigger_agent
    ]
)
