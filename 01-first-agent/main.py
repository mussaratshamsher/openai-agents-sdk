from dotenv import load_dotenv
import os
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, Agent, Runner, RunConfig
import asyncio

load_dotenv()

async def main():
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

    assistant = Agent(
        name="Assistant",
        instructions="Your job is to resolve queries",
        # model=model
    )

    while True:  # This loop will run continuously
        user_input = input("Enter your query here (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break  # Exit the loop if user types 'exit'
        
        result = await Runner.run(assistant, user_input, run_config=config)

        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())