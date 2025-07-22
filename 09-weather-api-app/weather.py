# weather_app.py
import pydeck as pdk 
import os
import requests
import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from agents.tool import function_tool
from io import StringIO
import base64

# Load environment variables
load_dotenv()

# --- Tool Function ---
@function_tool
def get_weather(city: str) -> str:
    """Fetches the current weather for a given city."""
    try:
        response = requests.get(
            f"http://api.weatherapi.com/v1/forecast.json?key=8e3aca2b91dc4342a1162608252604&q={city}&days=7&aqi=no&alerts=no",
            timeout=3
        )
        response.raise_for_status()
        data = response.json()
        current = data['current']
        return f"The current weather in {city} is {current['temp_c']}°C with {current['condition']['text']}."
    except Exception:
        return f"Sorry, I couldn't fetch the weather data for {city}. Please try again later."

@st.cache_data(ttl=600)
def fetch_weather_data(city):
    try:
        res = requests.get(
            f"http://api.weatherapi.com/v1/forecast.json?key=8e3aca2b91dc4342a1162608252604&q={city}&days=7&aqi=no&alerts=no",
            timeout=3
        )
        res.raise_for_status()
        forecast_data = res.json()
        return forecast_data['forecast']['forecastday'], forecast_data['location'], forecast_data['current']
    except Exception:
        return [], {}, {}

def download_weather_details(text, filename="weather_report.txt"):
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download Weather Report</a>'
    return href

# --- Agent Initialization ---
@st.cache_resource
def init_agent():
    MODEL_NAME = "gemini-2.0-flash"
    API_KEY = os.getenv("GEMINI_API_KEY")

    external_client = AsyncOpenAI(
        api_key=API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=external_client)

    return Agent(
        name="Weather Assistant",
        instructions="You are a helpful assistant who gives weather-related advice for the day.",
        model=model,
        tools=[get_weather]
    )

# --- UI Setup ---
st.set_page_config(page_title="Weather Assistant", page_icon="⛅")
st.markdown("""
    <style>
        .stApp {
             background: linear-gradient(45deg, #3e34c4, #9af4bd, #2f3581, #59f6b7);
        }
        .stButton > button {
            background: linear-gradient(45deg, #038203, #160646);
            color: white;
            width: 100%;
            font-size: 18px;
            font-weight: bold;
            padding: 12px;
            margin: 10px 0;
            border-radius: 8px;
        }
        .stSidebar {
            margin-top: 58px;
            background: linear-gradient(45deg, #3e34c4, #9af4bd, #2f3581, #59f6b7);
        }
        .stAlert {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #28a745;
        border-radius: 10px;
        shadow: 0 0 10px rgba(40, 167, 69, 0.5);
        padding: 10px;
        font-size: 20px;
        color: white !important;
    }
    .stAlert p {
        color: white !important;
    }
        .weather-column {
            text-align: center;
            padding: 10px;
            border-radius: 10px;
            background-color: rgba(255, 255, 255, 0.15);
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🌦️ Weather Assistant")
st.markdown("Get the current weather and forecast for your favorite city.")

# --- Sidebar ---
with st.sidebar:
    city_input = st.text_input("📍 Enter city name", value="Karachi")
    ask_button = st.button("🔍 Check Weather")
    show_hourly = st.checkbox("🕒 Show hourly forecast")
    unit = st.radio("🌡️ Temperature Unit", ["Celsius", "Fahrenheit"])

# --- Main Logic ---
if ask_button:
    st.snow()
    assistant = init_agent()
    question = f"What is the weather in {city_input}?"

    with st.spinner("⛅ Fetching weather details..."):
        result = asyncio.run(Runner.run(starting_agent=assistant, input=[{"role": "user", "content": question}]))

    st.success(result.final_output)
    st.markdown(download_weather_details(result.final_output), unsafe_allow_html=True)

# --- Forecast Section ---
if city_input:
    daily_data, location_data, current_weather = fetch_weather_data(city_input)

    if current_weather:
        st.subheader("🌞 Current Weather")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https:" + current_weather['condition']['icon'], width=80)
        with col2:
            st.markdown(f"### {current_weather['condition']['text']}")
            temp = current_weather['temp_c'] if unit == "Celsius" else (current_weather['temp_c'] * 9/5) + 32
            st.markdown(f"**Temperature:** {temp:.1f}°{unit[0]}")
            st.markdown(f"**Wind Speed:** {current_weather['wind_kph']} kph")
            st.markdown(f"**Feels Like:** {current_weather['feelslike_c']}°C")

        st.subheader("💡 Tips for Today")
        st.markdown("""
        - 🥤 Stay hydrated if it's hot.
        - ☔ Carry an umbrella if rain is expected.
        - 🧴 Use sunscreen on sunny days.
        - 🧥 Wear warm clothes if it's cold.
        - 🌫️ Check air quality before heading out if you’re sensitive.
        """)

    if daily_data:
        if show_hourly:
            st.subheader("🕒 Hourly Weather Forecast")
            hours_df = pd.DataFrame(daily_data[0]['hour'])
            hours_df['time'] = pd.to_datetime(hours_df['time']).dt.strftime('%I:%M %p')
            hours_df['temp'] = hours_df['temp_c'] if unit == "Celsius" else (hours_df['temp_c'] * 9/5) + 32

            fig = px.line(hours_df, x='time', y='temp', title='Hourly Temperature', markers=True)
            fig.update_traces(line=dict(color='skyblue'), marker=dict(size=6))
            st.plotly_chart(fig, use_container_width=True)

            # Map Section
            st.subheader("🌍 Location on Map")           
            lat, lon = location_data.get("lat"), location_data.get("lon")
            if lat and lon:
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=10)
          
            # Next, display the 3-day forecast
        st.subheader("📆 3-Day Weather Forecast")
        columns = st.columns(3, gap="small")
        for i in range(min(3, len(daily_data))):
            day = daily_data[i]
            date = day['date']
            condition = day['day']['condition']['text']
            icon_url = "https:" + day['day']['condition']['icon']
            max_temp = day['day']['maxtemp_c'] if unit == "Celsius" else (day['day']['maxtemp_c'] * 9/5) + 32
            min_temp = day['day']['mintemp_c'] if unit == "Celsius" else (day['day']['mintemp_c'] * 9/5) + 32
            wind = day['day']['maxwind_kph']

            with columns[i]:
                st.markdown(f"**{date}**")
                st.image(icon_url, width=48)
                st.markdown(f"{condition}")
                st.markdown(f"🌡️ {max_temp:.1f}° / {min_temp:.1f}°")
                st.markdown(f"💨 {wind} kph")
                st.markdown(f"**Humidity:** {day['day']['avghumidity']}%")
                st.markdown(f"**Rain Chance:** {day['day']['daily_chance_of_rain']}%")
