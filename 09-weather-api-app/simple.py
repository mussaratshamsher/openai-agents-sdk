
#weather app using weather api and agnets function tool
import os
import requests
import asyncio
import streamlit as st
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, RunConfig
from agents.tool import function_tool

# Load environment variables
load_dotenv()
set_tracing_disabled=True

# Define weather tool
@function_tool
def get_weather(city: str) -> str:
    """Fetches the current weather for a given city."""
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/current.json?key=8e3aca2b91dc4342a1162608252604&q={city}",
            timeout=2
        )
        response.raise_for_status()
        data = response.json()
        return f"The current weather in {city} is {data['current']['temp_c']}°C with {data['current']['condition']['text']}."
    except Exception:
        return f"Sorry, I couldn't fetch the weather data for {city}. Please try again later."

# Initialize agent
@st.cache_resource
def init_agent():
    MODEL_NAME = "gemini-2.0-flash"
    API_KEY = os.getenv("GEMINI_API_KEY")

    external_client = AsyncOpenAI(
        api_key=API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model = OpenAIChatCompletionsModel( model=MODEL_NAME, openai_client=external_client
    )

    config = RunConfig( model=model, model_provider=external_client, tracing_disabled=True
    )

    assistant = Agent(
        name="Weather Assistant",
        instructions="You are a helpful assistant who answers weather-related questions using tools.",
        model=model, tools=[get_weather]
    )

    return assistant

# App UI
st.set_page_config(page_title="Weather Assistant", page_icon="⛅")
st.title("🌦️ Weather Assistant")
st.markdown("Ask about the weather in any city. Powered by `openai-agent` SDK.")

st.markdown(
    """
    <style>               
        .stApp {
            background: linear-gradient(45deg, #3e34c4, #9af4bd, #2f3581, #59f6b7); /* Soft pastel colors */
            background-size: 400% 400%; 
            animation: gradientShift 10s ease infinite;
        }
        @keyframes gradientShift {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        /* Keyframes animation for the button */
        @keyframes pulse {  
            0% { box-shadow: 0 0 10px rgba(255, 87, 34, 0.7); }  
            50% { box-shadow: 0 0 20px rgba(255, 87, 34, 1); }  
            100% { box-shadow: 0 0 10px rgba(255, 87, 34, 0.7); }  
        }  
        /* Styling for the custom pulse button */
        .pulse-button {  
            display: block;  
            width: 100%;  
            text-align: center;  
            background: linear-gradient(45deg, #160646, #038203);  
            color: white;  
            font-size: 18px;  
            font-weight: bold;  
            padding: 12px;  
            margin: 10px 0;  
            border-radius: 8px;  
            text-decoration: none;  
            transition: all 0.3s ease-in-out;  
            animation: pulse 1.5s infinite;  
        }  
        /* Custom styling for streamlit's button */
        .stButton > button {
            background: linear-gradient(45deg, #038203, #160646);
            width: 100%;
            text-align: center;
            display: block;
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 12px;
            margin: 10px 0;
            border-radius: 8px;
            border: transparent;
            box-shadow: 
                0 0 10px rgb(232, 231, 231),
                0 0 20px rgb(232, 231, 231);
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease-in-out;
        }
        /* Animation for the moving border */
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 90%;
            height: 100%;
            color: transparent;
            border: 3px solid #FFC107;
            border-radius: 50%;
            transition: all 0.3s ease-in-out;
            transform: scale(0);
        }
        .stButton > button:hover {
            color: white;
            font: bold;
            padding: 12px;
            margin: 10px 0;
            border-radius: 8px;
            transition: all 0.3s ease-in-out;
            background: linear-gradient(45deg, #3a227c, #2f732f);
            box-shadow: 
                0 0 10px rgb(232, 231, 231),
                0 0 20px rgb(232, 231, 231), 
                0 0 40px rgb(232, 231, 231);
        }
        .stSidebar {
            margin-top: 58px;
            background: linear-gradient(45deg, #3e34c4, #9af4bd, #2f3581, #59f6b7);
            background-size: 400% 400%;
            animation: gradientShift 10s ease infinite;
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# Sidebar input
with st.sidebar:
    city_input = st.text_input("Enter city name", value="Karachi", help="Type a city to check its weather")
    ask_button = st.button("Check Weather 🌍")

# Session state to hold conversation history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Handle button click
if ask_button:
    st.snow()
    question = f"What is the weather in {city_input}?"
    st.session_state["history"].append({"role": "user", "content": question})

    assistant = init_agent()

    with st.spinner("Thinking..."):
        result = asyncio.run(Runner.run(
            starting_agent=assistant,
            input=st.session_state["history"]
        ))

    st.session_state["history"].append({"role": "assistant", "content": result.final_output})
    st.success(result.final_output)

# Show full conversation (optional)
if st.checkbox("Show full conversation history"):
    for msg in st.session_state["history"]:
        if msg["role"] == "user":
            st.markdown(f"🧑‍💬 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **Assistant:** {msg['content']}")
