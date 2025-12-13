class Agent:
    """
    Mock Google ADK Agent class.
    Simulates an LLM-powered agent that can use tools and delegate to sub-agents.
    """
    def __init__(self, name, model, description, instruction, tools=None, sub_agents=None, output_schema=None, output_key=None):
        self.name = name
        self.model = model
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        self.sub_agents = sub_agents or []
        self.output_schema = output_schema
        self.output_key = output_key

    def run(self, context):
        """
        Execute the agent with the given context.
        Context can be a WaferContext object or a dictionary.
        """
        print(f"\n{'='*60}")
        print(f"[Agent: {self.name}] Starting execution")
        print(f"{'='*60}")
        
        # Call tools if present
        results = {}
        if self.tools:
            for tool in self.tools:
                if hasattr(tool, 'agent'): 
                    # AgentTool wrapper
                    print(f"[{self.name}] 🔧 Delegating to sub-agent: {tool.agent.name}")
                    res = tool.agent.run(context)
                    results[tool.agent.output_key or tool.agent.name] = res
                elif hasattr(tool, 'func'):
                    # FunctionTool wrapper
                    print(f"[{self.name}] 🔧 Calling tool: {tool.name}")
                    res = tool.func(context)
                    results[tool.name] = res
        
        # Process sub_agents (direct agents, not wrapped)
        if self.sub_agents:
            for sa in self.sub_agents:
                if hasattr(sa, 'agent'): 
                    print(f"[{self.name}] 🔗 Delegating to: {sa.agent.name}")
                    res = sa.agent.run(context)
                    results[sa.agent.output_key or sa.agent.name] = res
                elif hasattr(sa, 'run'):
                    print(f"[{self.name}] 🔗 Delegating to: {sa.name}")
                    res = sa.run(context)
                    results[sa.name] = res
        
        print(f"[{self.name}] ✅ Finished")
        return results if results else context


class LoopAgent:
    """
    Mock Google ADK LoopAgent.
    Loops through sub-agents until a condition is met or max iterations reached.
    """
    def __init__(self, name, description, sub_agents, max_iterations=3, condition_key="is_valid"):
        self.name = name
        self.description = description
        self.sub_agents = sub_agents or []
        self.max_iterations = max_iterations
        self.condition_key = condition_key

    def run(self, context):
        print(f"\n{'#'*60}")
        print(f"[LoopAgent: {self.name}] Starting loop (max {self.max_iterations} iterations)")
        print(f"{'#'*60}")
        
        for i in range(self.max_iterations):
            print(f"\n[{self.name}] 🔄 Iteration {i+1}/{self.max_iterations}")
            
            # Run all sub-agents in sequence
            for sa in self.sub_agents:
                if hasattr(sa, 'agent'):
                    sa.agent.run(context)
                elif hasattr(sa, 'run'):
                    sa.run(context)
            
            # Check exit condition
            is_valid = False
            if hasattr(context, self.condition_key):
                is_valid = getattr(context, self.condition_key)
            elif isinstance(context, dict):
                is_valid = context.get(self.condition_key, False)
            
            if is_valid:
                print(f"[{self.name}] ✅ Condition met! Exiting loop.")
                break
            else:
                print(f"[{self.name}] ⚠️ Condition not met. {'Retrying...' if i < self.max_iterations-1 else 'Max iterations reached.'}")
        
        print(f"[{self.name}] Loop complete after {i+1} iteration(s)")
        return context


class SequentialAgent:
    """
    Mock Google ADK SequentialAgent.
    Runs sub-agents in sequence, passing context through.
    """
    def __init__(self, name, description, sub_agents):
        self.name = name
        self.description = description
        self.sub_agents = sub_agents or []
        self.output_key = name

    def run(self, context):
        print(f"\n[SequentialAgent: {self.name}] Running {len(self.sub_agents)} agents in sequence")
        
        for sa in self.sub_agents:
            if hasattr(sa, 'agent'):
                sa.agent.run(context)
            elif hasattr(sa, 'run'):
                sa.run(context)
        
        print(f"[{self.name}] Sequence complete")
        return context
