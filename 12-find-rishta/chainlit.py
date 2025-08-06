from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, function_tool
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
import chainlit as cl
import requests
import json

# Load env vars
load_dotenv()
set_tracing_disabled(True)

# Model Setup
API_KEY = os.getenv("GEMINI_API_KEY")
external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# Tool: Get User Data
@function_tool
def get_user_data(min_age: int, desired_gender: str) -> list[dict]:
    """Retrieve user data based on a minimum age and desired gender"""
    
users = [
    {"name": "Muneeb", "age": 22, "gender": "male", "home": "Lahore", "work": "Student", "phone": "+923001234567"},
    {"name": "Hania Ali", "age": 24, "gender": "female", "home": "Rawalpindi", "work": "Graphic Designer", "phone": "+923331234567"},
    {"name": "Zara Khan", "age": 26, "gender": "female", "home": "Karachi", "work": "Software Engineer", "phone": "+923001111111"},
    {"name": "Ali Raza", "age": 28, "gender": "male", "home": "Islamabad", "work": "Banker", "phone": "+923002222222"},
    {"name": "Fatima Noor", "age": 23, "gender": "female", "home": "Multan", "work": "Teacher", "phone": "+923003333333"},
    {"name": "Usman Javed", "age": 30, "gender": "male", "home": "Faisalabad", "work": "Business Owner", "phone": "+923004444444"},
    {"name": "Ayesha Malik", "age": 27, "gender": "female", "home": "Peshawar", "work": "Doctor", "phone": "+923005555555"},
    {"name": "Bilal Ahmed", "age": 25, "gender": "male", "home": "Hyderabad", "work": "Civil Engineer", "phone": "+923006666666"},
    {"name": "Noor Fatima", "age": 24, "gender": "female", "home": "Quetta", "work": "Pharmacist", "phone": "+923007777777"},
    {"name": "Ahmed Hassan", "age": 29, "gender": "male", "home": "Sialkot", "work": "Marketing Manager", "phone": "+923008888888"}
]
    return [
        user for user in users
        if user["age"] >= min_age and user["gender"].lower() == desired_gender.lower()
    ]

# Tool: Send WhatsApp Message
@function_tool
def send_whatsapp_message(phone: str, message: str) -> str:
    """Send a WhatsApp message using UltraMsg API"""
    instance_id = os.getenv("WHATSAPP_INSTANCE_ID")
    token = os.getenv("WHATSAPP_API_TOKEN")
    api_url = os.getenv("API_URL")
    
    url = f"{api_url}/instance{instance_id}/messages/chat"
    payload = {
        "token": token,
        "to": phone,
        "body": message
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"❌ Failed to send message: {e}"
    
    return f"✅ Message sent successfully to {phone}!"

# Agent
assistant = Agent(
    name="Rishty Wali",
    instructions="""
    You are a matchmaking assistant. Help users find matches based on age and gender.
    Format the results clearly. If user wants to send details via WhatsApp, call send_whatsapp_message.
    """,
    model=model,
    tools=[get_user_data, send_whatsapp_message]
)

# Chainlit App
@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    await cl.Message("💘 Welcome to Rishty Wali! \nType something like: `Find a female aged 24+`").send()

@cl.on_message
async def main(message: cl.Message):
    await cl.Message("🤔 Finding the perfect match...").send()

    history = cl.user_session.get("history") or []
    history.append({"role": "user", "content": message.content})
    
    try:
        result = Runner.run_sync(
            starting_agent=assistant,
            input=history
        )
        response = result.final_output
    except Exception as e:
        response = f"⚠️ An error occurred: {e}"
    
    history.append({"role": "assistant", "content": response})
    cl.user_session.set("history", history)

    await cl.Message(content=response).send()
