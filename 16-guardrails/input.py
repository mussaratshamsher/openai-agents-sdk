# Input guardrail: run on the input to the agent
# Input guardrails run in 3 steps:
# First, the guardrail receives the input provided by the user.
# Next, the guardrail function runs to produce a GuardrailFunctionOutput, which is then wrapped in an InputGuardrailResult.
# Finally, we check if .tripwire_triggered is true. If true, an InputGuardrailTripwireTriggered exception is raised, so you can appropriately respond to the user or handle the exception.
import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    OpenAIChatCompletionsModel,
    TResponseInputItem,
    input_guardrail,
    set_tracing_disabled,
)
from pydantic import BaseModel

# Load environment variables
load_dotenv()
set_tracing_disabled(True)

# Setup Gemini model
API_KEY = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# --------- Output type from guardrail
class MathHomeWork(BaseModel):
    is_math_homework: bool
    reasoning: str

# ---------input Guardrail agent
math_homework_guardrail_agent = Agent(
    name="Math Homework Guardrail Agent",
    instructions=(
        "Check whether the user is asking to solve their math homework or an assignment question.\n"
        "If it's a direct request to solve a homework or assignment, set is_math_homework=True.\n"
        "If it's just a basic math calculation like '2+2' or 'what is 10 / 2?', set is_math_homework=False.\n"
        "Always provide clear reasoning."
    ),
    model=model,
    output_type=MathHomeWork
)

# --------- Guardrail function
@input_guardrail
async def math_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(math_homework_guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework
    )

# --------- Main answering agent
class MathResponse(BaseModel):
    response: str

math_solver_agent = Agent(
    name="Math Solver Agent",
    instructions="You are a helpful assistant. Solve basic math problems and return response like {\"response\": \"your answer\"}",
    model=model,
    input_guardrails=[math_input_guardrail],
    output_type=MathResponse
)

# --------- Main app
async def main():
    user_input = input("Enter your question: ")
    try:
        result = await Runner.run(starting_agent=math_solver_agent, input=user_input)
        print("✅ Agent Response:", result.final_output.response)

    except InputGuardrailTripwireTriggered as e:
        print("🚨 Input Guardrail Triggered!")
        print("Reasoning:", e.guardrail_result.output_info.reasoning)


