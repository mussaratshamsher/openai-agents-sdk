import streamlit as st
import os
import asyncio
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from agents.run import RunConfig
from pathlib import Path
import base64


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

# Step 3: Define the Translator Agents
urdu_translator_agent = Agent(
    name="Urdu Translator",
    handoff_description="Specialist agent for translating messages to Urdu",
    instructions="You translate the user's message to Urdu. Provide accurate translations and maintain the original meaning."
)
hindi_translator_agent = Agent(
    name="Hindi Translator",
    handoff_description="Specialist agent for translating messages to Hindi",
    instructions="You translate the user's message to Hindi. Provide accurate translations and maintain the original meaning."
)
arabic_translator_agent = Agent(
    name="Arabic Translator",
    handoff_description="Specialist agent for translating messages to Arabic",
    instructions="You translate the user's message to Arabic. Provide accurate translations and maintain the original meaning."
)
japanese_translator_agent = Agent(
    name="Japanese Translator",
    handoff_description="Specialist agent for translating messages to Japanese",
    instructions="You translate the user's message to Japanese. Provide accurate translations and maintain the original meaning."
)
french_translator_agent = Agent(
    name="French Translator",
    handoff_description="Specialist agent for translating messages to French",
    instructions="You translate the user's message to French. Provide accurate translations and maintain the original meaning."
)
english_translator_agent = Agent(
    name="English Translator",
    handoff_description="Specialist agent for translating messages to English",
    instructions="You translate the user's message to English. Provide accurate translations and maintain the original meaning."
)
spanish_translator_agent = Agent(
    name="Spanish Translator",
    handoff_description="Specialist agent for translating messages to Spanish",
    instructions="You translate the user's message to Spanish. Provide accurate translations and maintain the original meaning."
)
german_translator_agent = Agent(
    name="German Translator",
    handoff_description="Specialist agent for translating messages to German",
    instructions="You translate the user's message to German. Provide accurate translations and maintain the original meaning."
)
chinese_translator_agent = Agent(
    name="Chinese Translator",
    handoff_description="Specialist agent for translating messages to Chinese",
    instructions="You translate the user's message to Chinese. Provide accurate translations and maintain the original meaning."
)
italian_translator_agent = Agent(
    name="Italian Translator",
    handoff_description="Specialist agent for translating messages to Italian",
    instructions="You translate the user's message to Italian. Provide accurate translations and maintain the original meaning."
)

# Step 4: Triage Agent
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's request for translation."
    "If multi-language translation is asked by the user then you will give tasks to each relevant agent.",
    handoffs=[hindi_translator_agent, arabic_translator_agent, japanese_translator_agent, french_translator_agent, english_translator_agent, spanish_translator_agent, german_translator_agent, chinese_translator_agent, urdu_translator_agent, italian_translator_agent]
)

# Step 5: Streamlit UI with title, Image and Stylish Button
st.set_page_config(page_title="Multilingual Translation Assistant", page_icon="🤖", layout="wide")
st.title("Multilingual Translation Assistant")

st.markdown(
    """
    <style>    
    .stApp {
    padding: 0px;
    margin: 0px;
    background-image: linear-gradient(rgb(10, 11, 11),rgb(43, 42, 42),rgb(6, 131, 209));
    background-size: cover;
    background-position: center;
    color: white! important;
    }
     .stSidebar .stSelectbox div {
     color: rgb(89, 183, 241)! important;
    }
    .stTextArea textarea {
        color: white !important;
        background-color: #333 !important;  
    }
    .stButton>button {
        background-image: linear-gradient(rgb(38, 186, 249),rgb(14, 13, 13),rgb(6, 131, 209));
        color: white;
        font-size: 18px;
        padding: 12px 24px;
        border-radius: 50px;
        border: none;
        position: relative;
        overflow: hidden;
        transition: background-color 0.4s ease, transform 0.3s ease;
    }
    .stButton>button:before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 300%;
        height: 300%;
        background: linear-gradient(rgb(38, 186, 249),rgb(14, 13, 13),rgb(6, 131, 209));
        transform: rotate(45deg);
        z-index: -1;
        animation: wave 3s infinite;
        z-index: 0;
        border-radius: 50%;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        color: white;
    }
    @keyframes wave {
        0% {
            transform: translateX(0);
        }
        100% {
            transform: translateX(-100%);
        }
    }
    .stSidebar{
    padding: 0px;
    margin-top: 58px;
    padding: 14px;
   background-image: linear-gradient(rgb(10, 11, 11),rgb(43, 42, 42),rgb(6, 131, 209));
    color: white! important;
    }
    .stText {
            color: white! important;
            font-size: 18px;
        }
        
    </style>
    """, unsafe_allow_html=True)

# Sidebar for language selection
selected_language = st.sidebar.selectbox(
    "Select Language for Translation",
    ["Urdu", "Hindi", "Arabic", "Japanese", "French", "English", "Spanish", "German", "Chinese"]
)
# Input area for user message
message = st.text_area("Enter your message for translation:")

# Function to handle translation asynchronously
async def handle_translation(message, selected_language):
    # Set up the history
    history = [{"role": "user", "content": message}]

    # Select the correct agent based on the language
    if selected_language == "Urdu":
        selected_agent = urdu_translator_agent
    elif selected_language == "Hindi":
        selected_agent = hindi_translator_agent
    elif selected_language == "Arabic":
        selected_agent = arabic_translator_agent
    elif selected_language == "Japanese":
        selected_agent = japanese_translator_agent
    elif selected_language == "French":
        selected_agent = french_translator_agent
    elif selected_language == "English":
        selected_agent = triage_agent
    elif selected_language == "Spanish":
        selected_agent = triage_agent
    elif selected_language == "German":
        selected_agent = triage_agent
    elif selected_language == "Chinese":
        selected_agent = triage_agent       

    # Run the agent with streaming enabled
    result = Runner.run_streamed(selected_agent, history, run_config=config)

    # Stream the response token by token
    translated_text = ""
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            token = event.data.delta
            translated_text += token
            st.text(translated_text)  # Display the translation as it comes in

    return translated_text

# When user presses the 'Translate' button
if st.button('Translate'):
    if message:
        st.write(f"Translating message to {selected_language}...")
        st.subheader(f"Translation to {selected_language}:")

        # Run the async function in the event loop
        translated_text = asyncio.run(handle_translation(message, selected_language)) 
    else:
        st.error("Please enter a message to translate.")

