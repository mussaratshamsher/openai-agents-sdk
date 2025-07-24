

import chainlit as cl
import os
import asyncio
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from agents.run import RunConfig
from agents import FileSearchTool

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
# step 3: Agent
# creating a simple assisstant agent that can search files in a vector store
# vector store is a collection of documents that can be searched using embeddings
# In this example, we will use a file search tool that can search files in a vector store.
# here vector store have information about your services which will be provided when someone search about you..
agent = Agent(
    name="Assistant",
    instructions="""
        You are acting as me, the owner of this service. 
        Always speak in the first person, as if you are the person providing the service. 
        Be friendly, concise, and helpful. Clearly explain what I offer, answer questions, 
        and keep the conversation natural and tailored to the user's needs. 
        Ask clarifying questions if needed to better assist them.
    """,
    tools=[
        FileSearchTool( # FileSearchTool will only work with OpenAI API key,
            max_num_results=3,
            vector_store_ids=["YOUR_VECTOR_STORE_ID"],
        )
    ]
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

