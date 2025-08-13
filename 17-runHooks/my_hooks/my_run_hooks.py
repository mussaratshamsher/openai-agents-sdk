from agents import RunHooks, RunContextWrapper, Agent, Tool 
from typing import Any
import requests

class MyRunHooks(RunHooks):

    async def on_agent_start(self, context: RunContextWrapper, agent:Agent) ->None:
        """Called before the agent is invoked"""
        print("Agent RunHook started")
        print("Agent Name: ", agent.name)

    async def on_agent_end(self, context: RunContextWrapper, agent:Agent, output:Any) ->None:
        """Called after the agent is invoked"""
        print("Agent RunHook ended")
        print("Agent Name: ", agent.name)

    # async def on_handoff(self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent) -> None:
    #     """Called when a handoff occurs."""
    #     print("Run Hook handoff")
    #     print("From Agent: ", from_agent.name)
    #     print("To Agent: ", to_agent.name)
      
    # async def on_tool_start(self, context: RunContextWrapper, agent:Agent, tool: Tool) -> None:
    #     """Called before a tool is invoked."""
    #     print("tool RunHook started")
    #     print("Tool Name: ", tool)
        
    # async def on_tool_end(self, context: RunContextWrapper, agent:Agent, tool: Tool, output: Any) -> None:
    #     """Called after a tool is invoked."""
    #     print("tool RunHook ended")
    #     print("Tool Name: ", tool.name)    
    