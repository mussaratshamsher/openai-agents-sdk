
import chainlit as cl
import os
import asyncio
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner 
from dotenv import load_dotenv
from agents.run import RunConfig

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

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

my_assistant = Agent(
    name="Personal Assistant",
    instructions="You are a helpful personal assistant."
)

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="Welcome! How can I assist you today?").send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    
    msg = cl.Message(content="")
    await msg.send()

    history.append({"role": "user", "content": message.content})
    # Run the agent with streaming enabled
    result = Runner.run_streamed(my_assistant, history, run_config=config)

        # Stream the response token by token
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            token = event.data.delta
            await msg.stream_token(token)

          #exact code to implement streaming in sdk
    # async for event in result.stream_events():
    #     if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
    #         print(event.data.delta, end="", flush=True)
     
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    
    await cl.Message(content=response).send()

