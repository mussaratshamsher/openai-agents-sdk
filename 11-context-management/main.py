
import os
import asyncio
import chainlit as cl
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from agents.run import RunConfig
from agents.tool import function_tool
# 1. context via Input:
#2. Context Via Instruction: it increases cost burden because each time instruction will proceed to llm
# with user input and also decreases speed
#3. Context via tool-call: Ondemand context: info is passed only when user asks   # Rather than context tool is best to use
# with tool company info is passed
#4. Retrieval or web Search: matches for specific search and gives only that part in result


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
# Company Inforamtion

company_info = {
    "name": "MandAco Solutions",
    "email": "contact@mandacosolutions.com",
    "phone": +92 325 3469898,
    "work": "We provide professional software solutions including frontend, backend, and full-stack development. We also offer Figma-to-code conversion, web app design, and custom software services.",
    "social_links": [
        {"name": "LinkedIn","icon": "🔗", "url": "https://www.linkedin.com/company/mandacosolutions"},
        {"name": "Twitter", "icon": "🐦","url": "https://twitter.com/mandacosolutions"},
        {"name": "Instagram","icon": "📸", "url": "https://instagram.com/mandacosolutions" },
        {"name": "GitHub", "icon": "💻", "url": "https://github.com/mandacosolutions"},
        {"name": "Website", "icon": "🌐", "url": "https://www.mandacosolutions.com"}
    ]
}

# Tools
   #"""context via tool calling """
@function_tool
def fetch_company_info():
    return company_info.strip()

   # """web search tool"""
@fucntion_tool
def web_search(query:str, max_results:int = 5) -> list:
    """
    tool to perform a web search using Tavily API.
    Arg: 
       query (str): The search query.
       max_results (int): The maximum number of results to return.
    """
# Agent
company_agent = Agent(
    name="mandaco Solutions",
    description="mandaco Solutions is a company that specializes",
    #instructions="You are mandaco Solution's assistant." + company-info.strip(), #varible is passed in instruction to use context instruction
    #to use context tool 
    instructions="You are mandaco Solution's assistant."
    tools[fetch_company_info]
)
#step5: Chainlit integration

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="🚀 MandACo Solution. 🚀 \n\n Welcome! How can I assist you today?").send()

@cl.on_message
async def handle_message(message:cl.Message):
  
    history = cl.user_session.get("history")

    msg = cl.Message(content="")
    await msg.send()

    history.append({"role":"user", "content":message.content})
# Run the Triage Agent with the user's message and history with streaming enabled
    result = Runner.run_streamed(company_agent, history, run_config=config)

# Stream the response back to the user
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            token = event.data.delta
            await msg.stream_token(token)

# Append the final output to the history
    history.append({"role":"assistant", "content":result.final_output})
    cl.user_session.set("history", history)
    
