

import chainlit as cl
import os
import asyncio
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from agents.run import RunConfig

load_dotenv()
#step1
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
#step2
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)
#step3: multi agents
urdu_translator_agent = Agent(
    name="Urdu Translator",
    handoff_description="Specialist agent for translating messages to Urdu",
    instructions="You translate the user's message to Urdu. Provide accurate translations and maintain the original meaning."
)
hindi_translator_agent = Agent(
    name="Hindi Translator",
    handoff_description="Specialist agent for translating messages to Hindi",
    instructions="You translate the user's message to Hindi. Provide accurate translations and maintain the original meaning.",
)
arabic_translator_agent = Agent(
    name="Arabic Translator",
    handoff_description="Specialist agent for translating messages to Arabic",
    instructions="You translate the user's message to Arabic. Provide accurate translations and maintain the original meaning.",
)
japanese_translator_agent = Agent(
    name="Japanese Translator",
    handoff_description="Specialist agent for translating messages to Japanese",
    instructions="You translate the user's message to Japanese. Provide accurate translations and maintain the original meaning.",
)
french_translator_agent = Agent(
    name="French Translator",
    handoff_description="Specialist agent for translating messages to French",
    instructions="You translate the user's message to French. Provide accurate translations and maintain the original meaning.",
)

# step 4: Triage Agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's request for translation."
    "If multi language translation is asked by the user then you will give task to each relevent agent.",
    handoffs=[hindi_translator_agent, arabic_translator_agent, japanese_translator_agent, french_translator_agent]
)
#step5`

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
    result = Runner.run_streamed(triage_agent, history, run_config=config)

        # Stream the response token by token
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            token = event.data.delta
            await msg.stream_token(token)
     
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)

