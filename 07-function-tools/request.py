import os
import asyncio
import requests
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, RunConfig
from agents.tool import function_tool
import chainlit as cl

# Load environment variables from .env file
load_dotenv()

# Define a tool function to fetch weather by city
@function_tool
def get_weather(city: str) -> str:
    """Fetches the current weather for a given city."""
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key=8e3aca2b91dc4342a1162608252604&q={city}",
            timeout=2
        )
        response.raise_for_status()
        data = response.json()
        return f"The current weather in {city} is {data['current']['temp_c']}°C with {data['current']['condition']['text']}."
    except Exception as e:
        return f"Sorry, I couldn't fetch the weather data for {city}. Please try again later."

# Chainlit chat start handler
@cl.on_chat_start
async def start():
    MODEL_NAME = "gemini-2.0-flash"
    API_KEY = os.getenv("GEMINI_API_KEY")

    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")

    # Setup external Gemini-compatible OpenAI client
    external_client = AsyncOpenAI(
        api_key=API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Define the model
    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=external_client
    )

    # Optional config for tracing
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    # Set up conversation history
    cl.user_session.set("history", [])

    # Create the weather assistant agent
    assistant = Agent(
        name="Weather Assistant",
        instructions="You are a helpful assistant who answers weather-related questions using tools.",
        model=model,
        tools=[get_weather]
    )

    # Store the agent in user session
    cl.user_session.set("assistant", assistant)

    # Send welcome message
    await cl.Message(content="⛅☔ Welcome! Ask me about the weather in any city. 🌍").send()

# Chainlit message handler
@cl.on_message
async def main(message: cl.Message):
    # Display interim thinking message
    msg = await cl.Message(content="Thinking...").send()

    # Get the assistant and conversation history
    assistant = cl.user_session.get("assistant")
    history = cl.user_session.get("history") or []

    # Add the user's message to history
    history.append({"role": "user", "content": message.content})

    # Run the assistant with full history
    result = await Runner.run(
        starting_agent=assistant,
        input=history,
    )

    # Add the assistant's response to history
    history.append({"role": "assistant", "content": result.final_output})

    # Update stored history
    cl.user_session.set("history", history)

    # Update the message with assistant response
    msg.content = result.final_output
    await msg.update()
