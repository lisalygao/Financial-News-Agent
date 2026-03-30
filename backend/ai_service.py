"""
AI Service — News fetching + analysis.

HOW TO CONNECT VERTEX AI GEMINI
================================
1. In Cloud Run, set these two environment variables:
     GOOGLE_CLOUD_PROJECT  = your-gcp-project-id   (e.g. "my-project-123456")
     GOOGLE_CLOUD_LOCATION = us-central1            (optional, defaults to us-central1)
   Cloud Run's service account also needs the "Vertex AI User" IAM role.

2. Uncomment the ENTIRE block below (lines marked with #).

3. In each placeholder function, replace the function body with the Gemini
   call shown inside its "--- Vertex AI Gemini replacement ---" docstring.

That's it — no other files need to change.
"""

import json
import random
import requests
from bs4 import BeautifulSoup

# ── Uncomment this entire block when wiring to Vertex AI ──────────────────────
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
        title = item.title.get_text(strip=True) if item.title else "No title"

        # <link> is the canonical article URL in RSS 2.0
        link_el = item.find("link")
        link = link_el.get_text(strip=True) if link_el and link_el.get_text(strip=True) else ""
        if not link:
            guid = item.find("guid")
            link = guid.get_text(strip=True) if guid else "#"

        # <source> holds the publisher name (e.g. "Wall Street Journal")
        source_el = item.find("source")
        source = source_el.get_text(strip=True) if source_el else ""

        articles.append({"title": title, "url": link, "source": source})
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
    Return a 6-8 sentence article summary as a list of sentences.

    --- Vertex AI Gemini replacement ---
    response = _model.generate_content(
        f"Write a 6-8 sentence objective summary of a financial news article "
        f"with this headline. Cover the key facts, context, market implications, "
        f"and any notable risks or opportunities. Write in clear, plain English "
        f"suitable for a general investor audience.\\n\\nHeadline: {headline}"
    )
    return [s.strip() for s in response.text.strip().split('. ') if s.strip()]
    """
    return [
        f"This article covers recent developments related to: {headline[:80]}.",
        "Markets have been closely monitoring this situation amid broader macroeconomic uncertainty.",
        "Sector analysts note that such developments often trigger short-term volatility before prices stabilise.",
        "Trading volumes and options activity suggest elevated investor interest in the affected securities.",
        "The Federal Reserve's current policy stance adds an additional layer of complexity to the outlook.",
        "Institutional investors are reassessing portfolio allocations in light of the latest information.",
        "Retail investor sentiment, as measured by survey data and social media signals, remains mixed.",
        "Connect Vertex AI Gemini to generate a real, article-specific summary here.",
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
    # Scale: 0 = Max Bearish (most negative), 100 = Max Bullish (most positive)
    # Positive news → high score → Bullish → Green
    # Negative news → low score  → Bearish → Red
    score = random.randint(0, 100)
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
            "source":          article["source"],
            "summary":         ai_generate_summary(article["title"]),
            "analysis_steps":  ai_generate_analysis_steps(article["title"]),
            "sentiment_label": sentiment["label"],
            "sentiment_score": sentiment["score"],
        })
    return results
