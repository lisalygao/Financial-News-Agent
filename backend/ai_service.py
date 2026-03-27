"""
AI Service — News fetching + analysis.

HOW TO CONNECT VERTEX AI GEMINI
================================
1. Add your Google Cloud project credentials to the deployment environment:
     GOOGLE_CLOUD_PROOGLE_OLOUD_JCT=yourojecmy-first-app-491201E_APPLICATION_CREDENTIALS=/path/to/service-account.json   (or use Workload Identity)

2. Uncomment the three imports at the top of this file.2
3. Replace each placeholder function body with the Gemini call shown in its
   "--- Vertex AI Gemini replacement ---" docstring block.

That's it — no other files need to change.
"""

import json
import random
import requests
from bs4 import BeautifulSoup

# ── Uncomment these three lines when wiring to Vertex AI ──────────────────────
# import os
# import vertexai
# from vertexai.generative_models import GenerativeModel
#
# vertexai.init(
#     project=os.environ["GOOGLE_CLOUD_PROJECT"],
#     location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
# )
# _model = GenerativeModel("gemini-2.5-flash")
# ─────────────────────────────────────────────────────────────────────────────


# ── RSS Fetcher ───────────────────────────────────────────────────────────────

def fetch_rss_news() -> list[dict]:
    """Fetch the top 5 financial headlines from Google News RSS."""
    url = (
        "https://news.google.com/rss/search"
        "?q=stock+market+financial+news&hl=en-US&gl=US&ceid=US:en"
    )
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item", limit=5)
    articles = []
    for item in items:
        title = item.title.text if item.title else "No title"
        guid  = item.find("guid")
        link  = guid.text.strip() if guid and guid.text else "#"
        articles.append({"title": title, "url": link})
    return articles


# ── AI Placeholder Functions ──────────────────────────────────────────────────
# Each function below is ready for a Vertex AI Gemini drop-in replacement.
# The exact code to use is shown inside each docstring.

def ai_generate_summary(headline: str) -> str:
    """
    Generate a 2-3 sentence plain-English summary of the headline.

    --- Vertex AI Gemini replacement ---
    response = _model.generate_content(
        f"Summarize this financial headline in 2-3 clear sentences for a "
        f"general audience:\\n{headline}"
    )
    return response.text.strip()
    """
    return (
        f"[AI Placeholder] '{headline[:70]}...' signals potential movement in "
        "equity markets. Analysts are watching closely for broader sector "
        "implications. Connect Vertex AI Gemini to generate real summaries."
    )


def ai_generate_analysis_steps(headline: str) -> list[str]:
    """
    Return a list of 5 step-by-step reasoning strings used to reach the summary.

    --- Vertex AI Gemini replacement ---
    response = _model.generate_content(
        f"For this financial headline, list exactly 5 numbered reasoning steps "
        f"an analyst would use to evaluate its market impact. "
        f"Output one step per line, no bullet points.\\n{headline}"
    )
    lines = [l.strip() for l in response.text.strip().splitlines() if l.strip()]
    return lines[:5]
    """
    return [
        "Identify the key market actors, sectors, and instruments mentioned.",
        "Assess the macroeconomic backdrop and recent trend context.",
        "Evaluate potential short-term price impact on major indices (S&P 500, Nasdaq).",
        "Consider investor sentiment signals: trading volume, options activity, VIX.",
        "Synthesise findings into an overall risk/reward outlook.",
    ]


def ai_get_sentiment(headline: str) -> dict:
    """
    Return overall market sentiment as {"label": str, "score": int 0-100}.
    Label is one of: "Bullish", "Neutral", "Bearish".

    --- Vertex AI Gemini replacement ---
    response = _model.generate_content(
        f"Rate the market sentiment of this headline on a scale of 0-100 "
        f"(0=very bearish, 50=neutral, 100=very bullish). "
        f"Reply with JSON only, no markdown: "
        f'{{\"label\": \"Bullish\", \"score\": 72}}\\n{headline}'
    )
    import re
    match = re.search(r'\\{{.*?\\}}', response.text, re.DOTALL)
    data = json.loads(match.group()) if match else {{}}
    label = data.get("label", "Neutral")
    score = int(data.get("score", 50))
    if label not in ("Bullish", "Neutral", "Bearish"):
        label = "Bullish" if score >= 60 else ("Bearish" if score <= 40 else "Neutral")
    return {{"label": label, "score": score}}
    """
    score = random.randint(20, 80)
    label = "Bullish" if score >= 60 else ("Bearish" if score <= 40 else "Neutral")
    return {"label": label, "score": score}


# ── Main pipeline (called by scheduler + /api/news/refresh) ───────────────────

def analyze_news() -> list[dict]:
    """
    Fetch the latest 5 financial headlines and run full AI analysis.
    Called automatically by the 7 AM PST scheduler and the Refresh button.
    """
    articles = fetch_rss_news()
    results = []
    for article in articles:
        sentiment = ai_get_sentiment(article["title"])
        results.append({
            "title":           article["title"],
            "url":             article["url"],
            "summary":         ai_generate_summary(article["title"]),
            "analysis_steps":  ai_generate_analysis_steps(article["title"]),
            "sentiment_label": sentiment["label"],
            "sentiment_score": sentiment["score"],
        })
    return results
