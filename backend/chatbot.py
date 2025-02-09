import os
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from backend.config import GOOGLE_API_KEY

# Set API Key for Google Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

FAISS_BASE_DIR = "models/faiss_index"
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

def load_faiss_index(ticker):
    """Loads FAISS index for a specific stock ticker."""
    ticker_index_path = os.path.join(FAISS_BASE_DIR, ticker)
    if os.path.exists(ticker_index_path):
        return FAISS.load_local(ticker_index_path, embeddings, allow_dangerous_deserialization=True)
    return None

def chatbot_response(user_input, ticker="AAPL", chat_history=[]):
    """Handles chatbot queries with FAISS retrieval and properly includes the fetched context."""
    vectorstore = load_faiss_index(ticker)
    
    if vectorstore is None:
        return f"⚠️ FAISS Index not found for {ticker}. Please create it first."

    retriever = vectorstore.as_retriever()

    # **Retrieve relevant financial context from FAISS**
    retrieved_docs = retriever.get_relevant_documents(user_input)
    retrieved_context = "\n".join([doc.page_content for doc in retrieved_docs[:3]])  # Take top 3 relevant docs

    # **Format previous chat messages for context (last 5 messages)**
    formatted_history = "\n".join([f"{role}: {message}" for role, message in chat_history[-5:]])

    # **Create prompt template to include both retrieved data & chat history**
    prompt_template = PromptTemplate(
        template="""
        You are an expert financial analyst. Use the provided financial data to answer user questions.

        **Relevant Financial Data Retrieved:**
        {context}

        **Previous Conversation Context:**
        {history}

        **User Question:**
        {question}

        Please provide a clear, concise, and well-reasoned answer.
        """,
        input_variables=["context", "history", "question"]
    )

    # **Apply the prompt template**
    formatted_prompt = prompt_template.format(context=retrieved_context, history=formatted_history, question=user_input)

    # Initialize Retrieval-QA Chain
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    # Get response from RAG pipeline
    response = qa.invoke(formatted_prompt)
    return response["result"]