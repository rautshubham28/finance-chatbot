import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("⚠️ Google API Key is missing! Please set GOOGLE_API_KEY in the .env file.")
