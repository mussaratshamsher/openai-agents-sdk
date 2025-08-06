import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from openai import AsyncOpenAI
import requests

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

# Define tools
@function_tool
def get_user_data(min_age: int, desired_gender: str) -> list[dict]:
    """Get user data based on age and gender."""
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
    return [user for user in users if user["age"] >= min_age and user["gender"].lower() == desired_gender.lower()]

@function_tool
def send_whatsapp_message(phone: str, message: str) -> str:
    """Send WhatsApp message via UltraMsg API."""
    instance_id = os.getenv("WHATSAPP_INSTANCE_ID")
    token = os.getenv("WHATSAPP_API_TOKEN")
    api_url = os.getenv("API_URL")

    url = f"{api_url}/instance{instance_id}/messages/chat"
    payload = {"token": token, "to": phone, "body": message}

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"❌ Error sending message: {e}"

    return f"✅ Message sent to {phone}!"

# Create the Agent
assistant = Agent(
    name="Rishty Wali",
    instructions="""
    You are a matchmaking agent. Help users find matches based on age and gender.
    Format results clearly. You can also send details via WhatsApp using the provided tool.
    """,
    model=model,
    tools=[get_user_data, send_whatsapp_message]
)

# Async wrapper
async def run_agent(user_history):
    result = await Runner.run(starting_agent=assistant, input=user_history)
    return result.final_output

# Streamlit UI
st.set_page_config(page_title="💘 Rishty Wali")
st.title("💘 Rishty Wali - Matchmaker Agent")
st.markdown("👋 Welcome! Enter your query & whatsapp to receive details (e.g.'Find females aged 24 and above & send details on +928978643234')")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("🔍 Enter your matchmaking query")

if st.button("🔎 Find Match"):
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.spinner("🔍 Finding the best match..."):
        try:
            output = asyncio.run(run_agent(st.session_state.history))
            st.session_state.history.append({"role": "assistant", "content": output})
            st.success("✅ Match found!")

            # Display output as markdown
            st.markdown("### 🗣️ Assistant Reply")
            st.markdown(f"```markdown\n{output}\n```")

            # Extract and display phone numbers with send button
            st.markdown("### 📤 Send Match Info via WhatsApp")

            lines = output.splitlines()
            for line in lines:
                if "Phone" in line or "phone" in line:
                    phone = line.split(":")[-1].strip()
                    if st.button(f"📱 Send to {phone}", key=phone):
                        message_status = send_whatsapp_message(phone=phone, message=output)
                        st.success(message_status)

        except Exception as e:
            st.error(f"❌ Error: {e}")
