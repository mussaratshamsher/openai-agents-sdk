# Output guardrails: run on the output of the agent
# Output guardrails run in 3 steps:
# First, the guardrail receives the output produced by the agent.
# Next, the guardrail function runs to produce a GuardrailFunctionOutput, which is then wrapped in an OutputGuardrailResult
# Finally , we check if .tripwire_triggered is true. If true, an OutputGuardrailTripwireTriggered exception is raised, so you can appropriately respond to the user or handle the exception.

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    OpenAIChatCompletionsModel,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
    set_tracing_disabled,
)

load_dotenv()
set_tracing_disabled(True)

API_KEY = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI(api_key=API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)
# --------- Output type from guardrail
class QueryResponse(BaseModel):
   response: str

class SensitiveWords(BaseModel):
    contains_sensitive_words: bool
    reasoning: str

# --------- Output Guardrail agent
output_guardrail_agent = Agent(
    name="Output Guardrail Checker",
    instructions=
        "Check if the response contains any sensitive or unethical words. "
        "If it does, set contains_sensitive_words=True and provide reasoning. "
        "If not, set contains_sensitive_words=False.",
    output_type=SensitiveWords,
    model=model
)
# ---------output Guardrail function
@output_guardrail
async def sensitive_words_guardrail(
    ctx:RunContextWrapper[None],agent:Agent,output:QueryResponse
    )->GuardrailFunctionOutput:

    result = await Runner.run(output_guardrail_agent, output.response, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.contains_sensitive_words
    )

    # Main Agent
assistant = Agent(
    name="Query Answering Agent",
    instructions="Answer the user's query while adhering to ethical guidelines.",
    output_guardrails=[sensitive_words_guardrail],
    model=model,
    output_type=QueryResponse
)    

# Main logic
async def main():
    user_query = input("Enter your query: ")
    try:
        result = await Runner.run(assistant, user_query)
        print(f"Response: {result.final_output}")
    except OutputGuardrailTripwireTriggered as e:
        print(f"Guardrail triggered: {e.message}")


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())

