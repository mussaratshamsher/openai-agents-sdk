import os 
import asyncio
import chainlit as cl
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from agents.run import RunConfig
from agents.tool import function_tool

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)    

model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=external_client
)

@function_tool("get_weather")
def get_weather(location: str, unit: str = "C") -> str:
    """Dummy weather tool"""
    return f"The weather in {location} is 22 degrees {unit}"

@cl.on_chat_start
async def on_chat_start():
    
    assistant = Agent(
        name="Weather Assistant",
        instructions="You respond to weather queries. You also respond to tell any location within a specific area. Show temperature in celsius and fahrenheit. Show suggestion to show temperature of next 24 hours. Show map of the area.",
        tools=[get_weather],
        model=model
    )

    cl.user_session.set("assistant", assistant)
    cl.user_session.set("history", [])

    await cl.Message(content="⛅☔ Check weather by Location. 🌍").send()

@cl.on_message
async def on_message(message: cl.Message):
    msg = await cl.Message(content="Thinking...").send()

    assistant = cl.user_session.get("assistant")
    history = cl.user_session.get("history") or []

    history.append({"role": "user", "content": message.content})

    result = await Runner.run(
        starting_agent=assistant,
        input=history,)

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    msg.content = result.final_output
    await msg.update()
