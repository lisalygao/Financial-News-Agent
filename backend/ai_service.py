"""
AI Service -- News fetching + analysis.

HOW TO CONNECT VERTEX AI GEMINI
================================
1. In Cloud Run, set these two environment variables:
     GOOGLE_CLOUD_PROJECT  = your-gcp-project-id   (e.g. "my-project-123456")
     GOOGLE_CLOUD_LOCATION = us-central1            (optional, defaults to us-central1)
   Cloud Run's service account also needs the "Vertex AI User" IAM role.

2. Set GOOGLE_CLOUD_PROJECT in your Cloud Run service environment variables.
   The app starts without it (using placeholder AI), and activates Vertex AI
   automatically once the variable is present.

3. In each placeholder function, replace the function body with the Gemini
   call shown inside its "--- Vertex AI Gemini replacement ---" docstring.

That's it -- no other files need to change.
"""

import json
import os
import random
import re
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Vertex AI initialisation -- CONDITIONAL on GOOGLE_CLOUD_PROJECT being set.
# The app starts and runs normally without it, using placeholder functions.
# Do NOT change os.environ.get() to os.environ[] -- that would crash on start.
# ---------------------------------------------------------------------------
_model = None
_gcp_project = os.environ.get("GOOGLE_CLOUD_PROJECT")
if _gcp_project:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    vertexai.init(
        project=_gcp_project,
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )
    _model = GenerativeModel("gemini-1.5-flash")


# Direct financial news RSS feeds -- real article URLs, no Google redirects.
_RSS_FEEDS = [
    ("Yahoo Finance", "https://finance.yahoo.com/rss/topfinstories"),
    ("CNBC",          "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("MarketWatch",   "https://feeds.marketwatch.com/marketwatch/topstories/"),
    ("Reuters",       "https://feeds.reuters.com/reuters/businessNews"),
    ("Investing.com", "https://www.investing.com/rss/news.rss"),
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def _is_absolute_url(url: str) -> bool:
    """Return True only if url is a full http/https URL -- never a relative path."""
    return url.startswith("http://") or url.startswith("https://")


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

            # Always prefer <link>; only fall back to <guid> if it is a full URL
            url = ""
            link_el = item.find("link")
            if link_el:
                url = link_el.get_text(strip=True)

            if not _is_absolute_url(url):
                guid = item.find("guid")
                guid_text = guid.get_text(strip=True) if guid else ""
                if _is_absolute_url(guid_text):
                    url = guid_text
                else:
                    continue

            # Drop any Google redirect links that slipped through
            if "google.com" in url:
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


# -- AI Functions --------------------------------------------------------------

def ai_generate_summary(headline: str) -> str:
    """
    Generate a 1-sentence summary of the headline.

    --- Vertex AI Gemini replacement ---
    response = _model.generate_content(
        f"In one sentence, explain the significance of this financial headline "
        f"for an investor: {headline}"
    )
    return response.text.strip()
    """
    if not _model:
        return "[AI Placeholder] Gemini not connected. Connect Vertex AI to generate real summaries."
    response = _model.generate_content(
        f"In one sentence, explain the significance of this financial headline "
        f"for an investor: {headline}"
    )
    return response.text.strip()


def ai_generate_analysis_steps(headline: str) -> list[str]:
    """
    Return 3 key highlights from the headline as a list of strings.

    --- Vertex AI Gemini replacement ---
    prompt = (
        f"Based on this financial headline: '{headline}', provide 3 brief "
        f"bullet-point highlights explaining the potential impact or context. "
        f"Return only the 3 points, no introductory text."
    )
    response = _model.generate_content(prompt)
    points = [re.sub(r'^[\\*\\-\\d\\.\\s]+', '', line).strip()
              for line in response.text.strip().split('\\n') if line.strip()]
    return points[:3]
    """
    if not _model:
        return [
            f"This article covers recent developments related to: {headline[:80]}.",
            "Markets have been closely monitoring this situation amid broader macroeconomic uncertainty.",
            "Connect Vertex AI Gemini to generate real, article-specific highlights here.",
        ]
    prompt = (
        f"Based on this financial headline: '{headline}', provide 3 brief "
        f"bullet-point highlights explaining the potential impact or context. "
        f"Return only the 3 points, no introductory text."
    )
    response = _model.generate_content(prompt)
    points = [re.sub(r'^[\*\-\d\.\s]+', '', line).strip()
              for line in response.text.strip().split('\n') if line.strip()]
    return points[:3] if points else [headline]


def ai_get_sentiment(headline: str) -> dict:
    """
    Return overall market sentiment as {"label": str, "score": int 0-100}.
    Label is one of: "Bullish", "Neutral", "Bearish".

    --- Vertex AI Gemini replacement ---
    prompt = (
        f'Analyze the market sentiment of this headline: "{headline}"\\n'
        f"RULES:\\n"
        f"- 0-40 score: BEARISH (bad news, markets likely to drop)\\n"
        f"- 41-59 score: NEUTRAL (mixed news)\\n"
        f"- 60-100 score: BULLISH (good news, growth, earnings beats)\\n"
        f'Return ONLY a JSON object: {{"label": "Bullish/Bearish/Neutral", "score": integer}}'
    )
    response = _model.generate_content(prompt)
    match = re.search(r'\\{{.*?\\}}', response.text, re.DOTALL)
    data = json.loads(match.group()) if match else {{}}
    label = data.get("label", "Neutral")
    score = int(data.get("score", 50))
    if label not in ("Bullish", "Neutral", "Bearish"):
        label = "Bullish" if score >= 60 else ("Bearish" if score <= 40 else "Neutral")
    return {{"label": label, "score": score}}
    """
    if not _model:
        score = random.randint(0, 100)
        label = "Bullish" if score >= 60 else ("Bearish" if score <= 40 else "Neutral")
        return {"label": label, "score": score}

    prompt = (
        f'Analyze the market sentiment of this headline: "{headline}"\n'
        f"RULES:\n"
        f"- 0-40 score: BEARISH (bad news, markets likely to drop)\n"
        f"- 41-59 score: NEUTRAL (mixed news)\n"
        f"- 60-100 score: BULLISH (good news, growth, earnings beats)\n"
        f'Return ONLY a JSON object: {{"label": "Bullish/Bearish/Neutral", "score": integer}}'
    )
    try:
        response = _model.generate_content(prompt)
        match = re.search(r'\{.*?\}', response.text, re.DOTALL)
        data = json.loads(match.group()) if match else {}
        label = data.get("label", "Neutral")
        score = int(data.get("score", 50))
        if label not in ("Bullish", "Neutral", "Bearish"):
            label = "Bullish" if score >= 60 else ("Bearish" if score <= 40 else "Neutral")
        return {"label": label, "score": score}
    except Exception:
        return {"label": "Neutral", "score": 50}


# -- Main pipeline (called by scheduler + /api/news/refresh) -------------------

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
