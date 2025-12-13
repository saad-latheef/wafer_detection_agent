from google.adk.agents import LoopAgent
from google.adk.tools.agent_tool import AgentTool

from agents.detection_agent import detection_agent
from agents.analysis_agent import analysis_agent
from agents.validation_agent import validation_agent


# Create the Detection Loop Agent using ADK's LoopAgent
# This will loop through Detection -> Analysis -> Validation
# until validation passes (is_valid = True) or max iterations reached

detection_loop_agent = LoopAgent(
    name="detection_loop_agent",
    description="Loops through detection, analysis, and validation until results are satisfactory.",
    sub_agents=[
        detection_agent,
        analysis_agent,
        validation_agent
    ],
    max_iterations=3,
    condition_key="is_valid"
)
