from fastapi import FastAPI
import os
from backend.chatbot import chatbot_response
from backend.faiss_store import create_faiss_index

app = FastAPI()

# Dictionary to store chat history for multiple threads
chat_threads = {}

@app.get("/chatbot")
def chatbot(query: str, ticker: str = "AAPL", thread_id: str = None):
    """Fetch chatbot response and maintain chat history using thread ID."""
    
    # Initialize thread if not exists
    if thread_id not in chat_threads:
        chat_threads[thread_id] = []

    # Get previous messages as context
    chat_history = chat_threads[thread_id]

    # Fetch chatbot response with history
    response = chatbot_response(query, ticker, chat_history)

    # Update chat history
    chat_threads[thread_id].append(("User", query))
    chat_threads[thread_id].append(("AI", response))

    return {"query": query, "ticker": ticker, "thread_id": thread_id, "response": response}

@app.get("/fetch_data")
def fetch_data(ticker: str):
    """Fetch new financial data and create a FAISS index if missing."""
    faiss_path = os.path.join("models/faiss_index", ticker)
    
    # Only fetch data if it doesn't exist
    if not os.path.exists(faiss_path):
        create_faiss_index(ticker)
        return {"status": "success", "message": f"Data fetched and FAISS index created for {ticker}."}
    
    return {"status": "exists", "message": f"Data already exists for {ticker}."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
