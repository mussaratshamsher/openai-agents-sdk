from agents import AgentHooks, RunContextWrapper, Agent, Tool 
from typing import Any
import requests

class MyAgentHooks(AgentHooks):

    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        """It runs before agent is invoked."""
        print("started agent Hook")
        # to check context here, pass context in main.py n print here
        print("Start Agent:", agent.name)
        print("Start Context:", context.context)
        # context.context["name"] = "Test"

        # To fetch data from api using context id in main agent
        # url = f"https://jsonplaceholder.typicode.com/users/{context.context['id']}"
        # res = requests.get(url)
        # result = res.json()
        # context.context["obj"] = result


    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        """It runs after agent is invoked."""
        print("End agent hook")
        print("End Agent:", agent.name)
        print("End Context:", context.context)

    # async def on_tool_start(self, context: RunContextWrapper, agent:Agent, tool: Tool,) -> None:
    #     """Called before a tool is invoked."""  
    #     print("Started tool Hook")
    # async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool: Tool, output: Any) -> None:
    #     """Called after tool is invoked."""
    #     print("Ended tool Hook")

    # async def on_handoff(self, context: RunContextWrapper, agent: Agent, source: Agent) -> None:
    #     """Called when the agent  is being off to. The source is the agent thai is handling
    #     off to this agent."""
    #     print("Handoff Hook")


   