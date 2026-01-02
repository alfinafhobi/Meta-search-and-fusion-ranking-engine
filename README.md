Metasearch + Fusion Ranking Engine

A Streamlit-based metasearch engine that fetches search results from multiple search engines (Google, Bing, DuckDuckGo, Yahoo via SerpApi), and fuses them into a single ranked list using information retrieval fusion techniques like Reciprocal Rank Fusion (RRF) and CombSUM.

* Features

Query multiple search engines simultaneously

* Fusion ranking algorithms:

Reciprocal Rank Fusion (RRF)

CombSUM

 Automatic URL de-duplication

 Configurable number of results per source

 Modular design (easy to add new sources or fusion methods)

 Streamlit UI for interactive exploration

* Project Structure
.
├── app.py               # Streamlit application (UI + flow)
├── config.py            # Environment variable & engine configuration
├── sources.py           # Search engine adapters (SerpApi, Google CSE)
├── fusion.py            # Fusion ranking algorithms
├── utils.py             # Utilities (deduplication, normalization)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .gitignore
└── LICENSE

* Setup Instructions
1. Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4️. Configure environment variables

Fill in your API keys:

GOOGLE_CSE_API_KEY=""
GOOGLE_CSE_CX=""
SERPAPI_KEY=""


- Running the Application
streamlit run app.py


The app will open in your browser.

* Configuration

You can enable/disable search engines in config.py:

ENABLED_ENGINES = [
    "google_cse",
    "serpapi_google",
    "serpapi_bing",
    "serpapi_duckduckgo",
    "serpapi_yahoo",
]

* Fusion Methods Explained
🔹 Reciprocal Rank Fusion (RRF)

Combines rankings based on position:

<img width="273" height="86" alt="image" src="https://github.com/user-attachments/assets/0bb862ae-4baa-4f99-949a-f3354f02d958" />

Robust to noisy rankings

Works well when sources disagree

🔹 CombSUM

Sums raw scores (or 1/rank fallback) across sources.

* Fallback Mode

If no API keys are provided, the system automatically switches to mock search data, allowing:

UI testing

Fusion algorithm validation

* Technologies Used

Python

Streamlit

SerpApi

Google Custom Search API

Requests

dotenv

*  License

This project is licensed under the MIT License.
