import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel
from my_tool.my_tools import Add
from my_hooks.my_agent_hooks import MyAgentHooks

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)
#using on_handoff
# math_assistant = Agent(
#     name="Math Assistant",
#     instructions="You are helpful Teacher.",
#     model=model,
#     hooks=MyAgentHooks(),
#     tools=[Add]
# )

assistant = Agent(
    name="Assistant",
    instructions="You are helpful assistant.",
    model=model,
    hooks=MyAgentHooks(),
    # handoffs=[math_assistant],
)

