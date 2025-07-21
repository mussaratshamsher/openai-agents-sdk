import os 
import chainlit as cl
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key = GEMINI_API_KEY,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model = MODEL_NAME,
    openai_client = external_client
)

config = RunConfig(
    model = model,
    model_provider = external_client,
    tracing_disabled = True
)

my_assitant = Agent(
    name = "AI Assitant",
    instructions = "You are helpful assitant"
)

@cl.on_chat_start
async def start():
    await cl.Message(
        content="👋 Welcome to AI Assitant! Ask anything."
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    try:
        user_input = message.content
        result = await Runner.run(my_assitant,input = user_input, run_config=config)
        await cl.Message(content = result.final_output).send()
    except Exception as e:
        await cl.Message(content = f"❌ Error: {e}").send()


