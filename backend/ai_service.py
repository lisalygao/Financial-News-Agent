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

# ── Uncomment these json
import randomiring to Vertex AI ──────────────────────
import os
import vertexai
from vertexai.generative_models import GenerativeModel
#
vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
)
model = GenerativeModel("gemini-2.5-flash")
# ─────────────────────────────────────────────────────────────────────────────


# ── RSS Fetcher ───────────────────────────────────────────────────────────────

def fetch_rss_news() -> lisRSS Fetcher ───────────────────────────────────────────────────────────────

# Direct financial news RSS feeds — these publish real article URLs, no redirects.
_RSS_FEEDS = [
    ("Yahoo Finance",  "https://finance.yahoo.com/rss/topfinstories"),
    ("CNBC",           "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("MarketWatch",    "https://feeds.marketwatch.com/marketwatch/topstories/"),
    ("Reuters",        "https://feeds.reuters.com/reuters/businessNews"),
    ("Investing.com",  "https://www.investing.com/rss/news.rss"),
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def _fetch_feed(name: str, feed_url: str, limit: int) -> list[dict]:
    """Fetch up to `limit` articles from a single RSS feed."""
    try:
        r = requests.get(feed_url, timeout=8, headers=_HEADERS)
        soup = BeautifulSoup(r.content, "xml")
        articles = []
        for item in soup.find_all("item", limit=limit):
            title = item.title.get_text(strip=True) if item.title else ""
            if not title:
                continue

            # <link> in direct RSS feeds is the real article URL
            link_el = item.find("link")
            url = link_el.get_text(strip=True) if link_el else ""
            if not url:
                guid = item.find("guid")
                url = guid.get_text(strip=True) if guid else ""
            # Reject any google.com redirects that slipped through
            if not url or "google.com" in url:
                continue

            articles.append({"title": title, "url": url, "source": name})
        return articles
    except Exception as e:
        print(f"[RSS] Failed to fetch {name}: {e}")
        return []


def fetch_rss_news() -> list[dict]:
    """
    Fetch the top 5 financial headlines from direct publisher RSS feeds.
    Tries each feed in order and stops once 5 articles are collected.
    """
    collected: list[dict] = []
    for name, feed_url in _RSS_FEEDS:
        if len(collected) >= 5:
            break
        needed = 5 - len(collected)
        articles = _fetch_feed(name, feed_url, limit=needed)
        collected.extend(articles[:needed])

    return collected[:5]


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
            "source":          article["source ai_generate_analysis_steps(article["title"]),
            "sentiment_label": sentiment["label"],
            "sentiment_score": sentiment["score"],
        })
    return results
