"""
AI Service — News fetching + analysis.

The three AI_PLACEHOLDER functions below are ready to be replaced with
real Vertex AI Gemini calls. Each function is clearly documented with
the exact Gemini code you need to drop in.
"""

import random
import requests
from bs4 import BeautifulSoup


# ── RSS Fetcher ───────────────────────────────────────────────────────────────

def fetch_rss_news() -> list[dict]:
    """Fetch top 5 financial headlines from Google News RSS."""
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


# ── AI Placeholders ───────────────────────────────────────────────────────────
# TODO: Replace each function body with the Gemini call shown in the docstring.

def ai_generate_summary(headline: str) -> str:
    """
    Generate a 2-3 sentence plain-English summary of the headline.

    --- Vertex AI Gemini replacement ---
    import vertexai
    from vertexai.generative_models import GenerativeModel
    vertexai.init(project=os.environ["GOOGLE_CLOUD_PROJECT"], location="us-central1")
    model = GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(
        f"Summarize this financial headline in 2-3 clear sentences for a general audience:\\n{headline}"
    )
    return response.text.strip()
    """
    return (
        f"[AI Placeholder] This headline — '{headline[:70]}...' — signals potential "
        "movement in equity markets. Analysts are watching closely for broader sector "
        "implications. Connect Vertex AI Gemini to generate real summaries."
    )


def ai_generate_analysis_steps(headline: str) -> list[str]:
    """
    Return a list of step-by-step reasoning steps that led to the summary.

    --- Vertex AI Gemini replacement ---
    response = model.generate_content(
        f"For this financial headline, list 5 numbered reasoning steps an analyst "
        f"would use to evaluate its market impact. Output plain text, one step per line.\\n{headline}"
    )
    return [line.strip() for line in response.text.strip().split("\\n") if line.strip()]
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
    response = model.generate_content(
        f"Rate the market sentiment of this headline on a scale of 0-100 "
        f"(0=very bearish, 50=neutral, 100=very bullish). "
        f"Reply with JSON only: {{\"label\": \"Bullish\", \"score\": 72}}\\n{headline}"
    )
    import json, re
    match = re.search(r'\\{.*?\\}', response.text, re.DOTALL)
    return json.loads(match.group()) if match else {\"label\": \"Neutral\", \"score\": 50}
    """
    score = random.randint(20, 80)
    label = "Bullish" if score >= 60 else ("Bearish" if score <= 40 else "Neutral")
    return {"label": label, "score": score}


# ── Main pipeline ─────────────────────────────────────────────────────────────

def analyze_news() -> list[dict]:
    """
    Fetch the latest 5 financial headlines and run full AI analysis.
    Called by the scheduler (daily at 7 AM PST) and the /api/news/refresh endpoint.
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
