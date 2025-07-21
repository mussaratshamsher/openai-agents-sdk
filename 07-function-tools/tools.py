import os
import asyncio
from dotenv import load_dotenv
import chainlit as cl
import requests
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, RunConfig
from agents.tool import function_tool

# Load environment variables
load_dotenv()

# Dummy weather tool
@function_tool
def get_weather(city: str):
    """Returns dummy weather info for a city."""
    return f"The weather in {city} is sunny with a temperature of 25°C."

# On chat start
@cl.on_chat_start
async def start():
    MODEL_NAME = "gemini-2.0-flash"
    API_KEY = os.getenv("GEMINI_API_KEY")

    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

    # Setup Gemini-compatible OpenAI client
    external_client = AsyncOpenAI(
        api_key=API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=external_client
    )

    # Optional config (can be used for tracing/debugging)
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    # Create assistant agent
    assistant = Agent(
        name="Weather Assistant",
        instructions="You respond to weather queries.",
        model=model,
        tools=[get_weather]
    )

    # Store in session
    cl.user_session.set("assistant", assistant)
    cl.user_session.set("history", [])

    await cl.Message(content="⛅☔ Check weather by Location. 🌍").send()

# On each message
@cl.on_message
async def handle_message(message: cl.Message):
    msg = await cl.Message(content="Thinking...").send()

    assistant = cl.user_session.get("assistant")
    history = cl.user_session.get_
