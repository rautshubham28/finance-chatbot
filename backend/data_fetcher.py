import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import json

CIK_FILE = "data/cik_ticker_mapping.json"

def get_cik(ticker):
    """Fetch CIK code for a given stock ticker from JSON file."""
    try:
        with open(CIK_FILE, "r") as f:
            cik_data = json.load(f)
        return cik_data.get(ticker.upper(), None)
    except FileNotFoundError:
        return "CIK mapping file not found."


def get_stock_data(ticker):
    """Fetch stock price data for a given ticker."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    return hist[['Open', 'High', 'Low', 'Close', 'Volume']].tail().to_string()


def get_financial_news(ticker):
    """Fetch financial news using yfinance."""
    stock = yf.Ticker(ticker)
    news = stock.news  # Returns a list of news dictionaries
    return [(item['content']["title"], item['content']["summary"]) for item in news[:5]]


def fetch_financial_reports(ticker, concept="Assets"):
    """Fetch financial reports from SEC EDGAR API."""
    cik = get_cik(ticker)
    if not cik:
        return {"error": f"CIK not found for ticker {ticker}."}

    SEC_BASE_URL = "https://data.sec.gov/api/xbrl/companyconcept/CIK"
    url = f"{SEC_BASE_URL}{cik}/us-gaap/{concept}.json"
    headers = {"User-Agent": "YourEmail@example.com"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch data"}

