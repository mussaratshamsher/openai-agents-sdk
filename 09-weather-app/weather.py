# weather app using weather api and agents function tool
import os
import requests
import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, RunConfig
from agents.tool import function_tool

# Load environment variables
load_dotenv()

# Define weather tool
@function_tool
def get_weather(city: str) -> str:
    """Fetches the current weather for a given city."""
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/forecast.json?key=8e3aca2b91dc4342a1162608252604&q={city}&days=1",
            timeout=3
        )
        response.raise_for_status()
        data = response.json()
        current = data['current']
        return f"The current weather in {city} is {current['temp_c']}°C with {current['condition']['text']}."
    except Exception:
        return f"Sorry, I couldn't fetch the weather data for {city}. Please try again later."

# Function to get hourly weather
def fetch_hourly_weather(city):
    try:
        res = requests.get(
            f"http://api.weatherapi.com/v1/forecast.json?key=8e3aca2b91dc4342a1162608252604&q={city}&days=1",
            timeout=3
        )
        res.raise_for_status()
        forecast_data = res.json()
        return forecast_data['forecast']['forecastday'][0]['hour']
    except Exception:
        return []

# Initialize agent
@st.cache_resource
def init_agent():
    MODEL_NAME = "gemini-2.0-flash"
    API_KEY = os.getenv("GEMINI_API_KEY")

    external_client = AsyncOpenAI(
        api_key=API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=external_client)

    config = RunConfig(model=model, model_provider=external_client, tracing_disabled=True)

    assistant = Agent(
        name="Weather Assistant",
        instructions="You are a helpful assistant who answers weather-related questions using tools.",
        model=model,
        tools=[get_weather]
    )

    return assistant

# UI
st.set_page_config(page_title="Weather Assistant", page_icon="⛅")
st.title("🌦️ Weather Assistant")
st.markdown("Ask about the weather in any city. Powered by `openai-agent` SDK.")

# Sidebar
with st.sidebar:
    city_input = st.text_input("Enter city name", value="Karachi", help="Type a city to check its weather")
    ask_button = st.button("Check Weather 🌍")
    show_hourly = st.checkbox("Show hourly forecast")

# Session state to hold conversation history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Handle weather check
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

# Show hourly forecast
if show_hourly and city_input:
    hourly_data = fetch_hourly_weather(city_input)
    if hourly_data:
        st.subheader(f"📅 Hourly Forecast for {city_input}")

        selected_hour = st.select_slider(
            "Select Hour", 
            options=[f"{h['time'].split(' ')[1]}" for h in hourly_data], 
            value="12:00"
        )

        for hour in hourly_data:
            if selected_hour in hour['time']:
                st.write(f"### 🕒 {hour['time']}")
                st.image("http:" + hour["condition"]["icon"], width=60)
                st.write(f"🌡️ Temp: {hour['temp_c']} °C")
                st.write(f"💧 Humidity: {hour['humidity']}%")
                st.write(f"🌬️ Wind: {hour['wind_kph']} kph")
                st.write(f"☁️ Condition: {hour['condition']['text']}")
                break

        # Optional Chart
        st.markdown("#### 📊 Temperature Trend (Today)")
        df = pd.DataFrame(hourly_data)
        df['hour'] = df['time'].apply(lambda x: x.split(" ")[1])
        fig = px.line(df, x="hour", y="temp_c", title="Hourly Temperature (°C)", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Could not load hourly forecast.")

# Show full conversation
if st.checkbox("Show full conversation history"):
    for msg in st.session_state["history"]:
        if msg["role"] == "user":
            st.markdown(f"🧑‍💬 **You:** {msg['content']}")
        else:
            st.markdown(f"🤖 **Assistant:** {msg['content']}")
