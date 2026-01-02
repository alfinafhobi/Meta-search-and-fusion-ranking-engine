import os
from dotenv import load_dotenv

load_dotenv()

# Google Custom Search
GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY", "").strip()
GOOGLE_CSE_CX = os.getenv("GOOGLE_CSE_CX", "").strip()

# SerpApi
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "").strip()

ENABLED_ENGINES = [
    "google_cse",
    "serpapi_google",
    "serpapi_bing",
    "serpapi_duckduckgo",
    "serpapi_yahoo",  # ✅ Added SerpApi
]

