import os
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.data_fetcher import get_stock_data, get_financial_news, fetch_financial_reports
from backend.config import GOOGLE_API_KEY

# Set API Key for Google Gemini
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

FAISS_BASE_DIR = "models/faiss_index"
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def create_faiss_index(ticker="AAPL"):
    """Fetches financial data, converts it into embeddings, and stores in FAISS."""
    financial_reports = fetch_financial_reports(ticker, "Revenue") or "No financial report available"
    stock_data = get_stock_data(ticker) or "No stock data available"
    financial_news = get_financial_news(ticker) or []

    # Combine all documents
    all_documents = {
        "Stock Data": stock_data,
        "Financial News": "\n".join([f"{title}: {summary}" for title, summary in financial_news]),
        "Financial Reports": str(financial_reports)
    }

    combined_text = "\n".join([f"{key}: {value}" for key, value in all_documents.items()])

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = [Document(page_content=chunk) for chunk in text_splitter.split_text(combined_text)]

    # Define FAISS storage path for this ticker
    ticker_index_path = os.path.join(FAISS_BASE_DIR, ticker)
    os.makedirs(ticker_index_path, exist_ok=True)

    # Create and save FAISS index
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(ticker_index_path)
    print(f"✅ FAISS index saved for {ticker} at {ticker_index_path}")

if __name__ == "__main__":
    create_faiss_index("TSLA")  # Example for Tesla
