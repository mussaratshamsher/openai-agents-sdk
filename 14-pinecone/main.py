import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, function_tool
import chainlit as cl

# Load API keys from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Gemini setup
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 1024
INDEX_NAME = "sample-movies"

# Initialize Gemini embedding client
embedding_client = OpenAI(api_key=GEMINI_API_KEY, base_url=GEMINI_BASE_URL)

# Connect to Pinecone
pinecone = Pinecone(api_key=PINECONE_API_KEY)

def connect_pinecone_index():
    existing_indexes = [idx.name for idx in pinecone.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        pinecone.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")  # You can use any supported region
        )
        print(f"✅ Created new index: {INDEX_NAME}")
    else:
        print(f"ℹ️ Index '{INDEX_NAME}' already exists.")
    return pinecone.Index(INDEX_NAME)

# Connect to or create the index
pinecone_index = connect_pinecone_index()

# ✅ Upsert documents into Pinecone
def upsert_documents(index, docs):
    vectors = []
    print("📥 Generating embeddings...")
    for doc in docs:
        try:
            embedding = embedding_client.embeddings.create(
                model=GEMINI_EMBEDDING_MODEL,
                input=doc['text']
            ).data[0].embedding

            vectors.append({
                "id": doc['id'],
                "values": embedding,
                "metadata": {"text": doc['text']}
            })
        except Exception as e:
            print(f"❌ Error embedding document {doc['id']}: {e}")

    if vectors:
        print(f"📤 Upserting {len(vectors)} documents to Pinecone...")
        index.upsert(vectors=vectors)
        print("✅ Upsert complete.")
    else:
        print("⚠️ No valid vectors to upsert.")

# ✅ 10 example docs
docs = [
    {"id": "1", "text": "Gemini is a Google AI model used for code and reasoning tasks."},
    {"id": "2", "text": "Pinecone provides a vector database service for AI applications."},
    {"id": "3", "text": "Chainlit allows developers to build conversational UIs rapidly."},
    {"id": "4", "text": "Streamlit is used for building data apps using pure Python."},
    {"id": "5", "text": "OpenAI developed GPT models that revolutionized natural language processing."},
    {"id": "6", "text": "LangChain helps in building context-aware AI applications using chains."},
    {"id": "7", "text": "FastAPI is a modern Python web framework for building APIs quickly."},
    {"id": "8", "text": "Vector embeddings are numerical representations of text for semantic search."},
    {"id": "9", "text": "Gemini embeddings can be used to convert text into high-dimensional vectors."},
    {"id": "10", "text": "AI agents can use tools, memories, and planning to solve complex tasks."}
]

# 👇 Run this once to upload documents
upsert_documents(pinecone_index, docs)

# ✅ Tool for search using Gemini + Pinecone
@function_tool
def search_docs(query: str) -> str:
    embedding = embedding_client.embeddings.create(
        model=GEMINI_EMBEDDING_MODEL,
        input=query
    ).data[0].embedding

    results = pinecone_index.query(vector=embedding, top_k=3, include_metadata=True)

    if results.matches:
        return "\n".join([f"🔎 {m.metadata['text']}" for m in results.matches])
    return "❌ No relevant results found."

# ✅ Setup the agent
agent = Agent(
    model="models/gemini-2.0-flash",
    tools=[search_docs],
    system_message="You are a helpful AI with document memory using Pinecone."
)

# ✅ Chainlit hooks
@cl.on_chat_start
async def start_chat():
    cl.user_session.set("runner", Runner(agent))
    await cl.Message("✨ Gemini Agent is ready. Type your question.").send()

@cl.on_message
async def handle_message(msg: cl.Message):
    runner: Runner = cl.user_session.get("runner")
    response = await runner.run_async(msg.content)
    await cl.Message(content=response).send()
