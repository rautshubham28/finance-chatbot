import streamlit as st
import requests
import os
import uuid  # For generating unique thread IDs

# API URLs
API_URL = "http://127.0.0.1:8000/chatbot"
FETCH_DATA_URL = "http://127.0.0.1:8000/fetch_data"
FAISS_BASE_DIR = "models/faiss_index"

# Initialize session state for tracking conversations
if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = {}  # Stores chat history for multiple threads

if "active_thread" not in st.session_state:
    st.session_state["active_thread"] = None  # Stores the active chat thread

# Sidebar: Chat Management
st.sidebar.title("💬 Chat History")

# Create a new chat thread
if st.sidebar.button("➕ New Chat"):
    new_thread_id = str(uuid.uuid4())  # Generate unique thread ID
    st.session_state["chat_threads"][new_thread_id] = {"messages": [], "name": f"Conversation {len(st.session_state['chat_threads']) + 1}"}
    st.session_state["active_thread"] = new_thread_id

# Display chat threads in sidebar
if st.session_state["chat_threads"]:
    selected_thread = st.sidebar.radio(
        "Select a conversation:", 
        list(st.session_state["chat_threads"].keys()), 
        format_func=lambda t: st.session_state["chat_threads"][t]["name"]
    )
    st.session_state["active_thread"] = selected_thread

# Sidebar: Select Stock Ticker
st.sidebar.title("📈 Select Stock Ticker")
ticker = st.sidebar.selectbox("Choose a ticker:", ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"])

# Check if FAISS data exists locally
faiss_path = os.path.join(FAISS_BASE_DIR, ticker)
data_exists = os.path.exists(faiss_path)

# Option to choose between local data or fetching new data
fetch_option = st.sidebar.radio("Choose Data Source:", 
                                ["Use Local Data" if data_exists else "Fetch New Data", "Fetch New Data"])

# Fetch new data if required
if fetch_option == "Fetch New Data":
    st.sidebar.info(f"Fetching latest data for {ticker}...")
    response = requests.get(f"{FETCH_DATA_URL}?ticker={ticker}")
    if response.status_code == 200:
        st.sidebar.success(f"✅ Data fetched successfully for {ticker}!")
    else:
        st.sidebar.error("❌ Failed to fetch data.")

# Main Chat Window
st.title("💬 AI-Powered Financial Chatbot")

# Get the active thread
active_thread = st.session_state["active_thread"]
if active_thread not in st.session_state["chat_threads"]:
    st.session_state["chat_threads"][active_thread] = {"messages": [], "name": f"Conversation {len(st.session_state['chat_threads'])}"}

# User Input
user_input = st.text_input("Enter your financial question:")

if st.button("Ask"):
    if user_input:
        thread_id = st.session_state["active_thread"]
        
        # Send API request with thread context
        response = requests.get(f"{API_URL}?query={user_input}&ticker={ticker}&thread_id={thread_id}").json()
        
        # Store conversation history
        st.session_state["chat_threads"][thread_id]["messages"].append(("You", user_input))
        st.session_state["chat_threads"][thread_id]["messages"].append(("AI", response["response"]))

# Display chat history for the selected thread
for role, text in st.session_state["chat_threads"][st.session_state["active_thread"]]["messages"]:
    st.chat_message(role).write(text)
