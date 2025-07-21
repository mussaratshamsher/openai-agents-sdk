
import os
import asyncio
import chainlit as cl
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from agents.run import RunConfig

load_dotenv()
#step1 : Initialize the model and API key
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
#step2 : config
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

#step3: Tools

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples.",
)
# step 4: Triage Agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question. You will translate output also if user needs in any language.",
    handoffs=[history_tutor_agent, math_tutor_agent]
)
#step5: Chainlit integration

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="🚀 **🚨 HISTORY & MATH TUTOR 🚨** 🚀 \n\n Welcome! How can I assist you today?").send()

@cl.on_message
async def handle_message(message:cl.Message):
  
    history = cl.user_session.get("history")

    msg = cl.Message(content="")
    await msg.send()

    history.append({"role":"user", "content":message.content})
# Run the Triage Agent with the user's message and history with streaming enabled
    result = Runner.run_streamed(triage_agent, history, run_config=config)

# Stream the response back to the user
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            token = event.data.delta
            await msg.stream_token(token)

# Append the final output to the history
    history.append({"role":"assistant", "content":result.final_output})
    cl.user_session.set("history", history)
    
