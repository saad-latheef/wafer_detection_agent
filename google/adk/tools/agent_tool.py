class AgentTool:
    def __init__(self, agent):
        self.agent = agent
        self.name = f"tool_{agent.name}"
        self.description = agent.description

class FunctionTool:
    def __init__(self, func, name=None):
        self.func = func
        self.name = name or func.__name__
