import os
import re
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "my-first-app-491201")
model = None

def get_model():
    global model
    if model is None and PROJECT_ID:
        vertexai.init(project=PROJECT_ID, location="us-central1")
        model = GenerativeModel("gemini-2.5-flash")
    return model

def get_market_news():
    try:
        rss_url = "https://news.google.com/rss/search?q=stock+market+analysis&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(rss_url, timeout=10)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item", limit=5)
        articles = []
        for item in items:
            title = item.title.text if item.title else "No title"
            guid = item.find("guid")
            link = guid.text.strip() if guid and guid.text else "#"
            articles.append({"title": title, "link": link})
        return articles
    except Exception as e:
        print(f"Scraping Error: {e}")
        return []

def parse_sentiment(raw_text):
    """Extract the SENTIMENT_DATA JSON line from AI response."""
    match = re.search(r'SENTIMENT_DATA:\s*(\{.*?\})', raw_text)
    if match:
        try:
            data = json.loads(match.group(1))
            label = data.get("label", "Neutral")
            score = int(data.get("score", 50))
            return label, score
        except Exception:
            pass
    return "Neutral", 50

def strip_sentiment_line(raw_text):
    """Remove the SENTIMENT_DATA line from the display text."""
    return re.sub(r'SENTIMENT_DATA:\s*\{.*?\}\n?', '', raw_text).strip()

@app.route("/")
def index():
    articles = get_market_news()
    headlines = [a["title"] for a in articles]
    ai_analysis = ""
    sentiment_label = "Neutral"
    sentiment_score = 50

    if not articles:
        ai_analysis = "<p>Agent Error: Could not retrieve live headlines to analyze.</p>"
    else:
        headlines_payload = "\n".join([f"{i+1}. {h}" for i, h in enumerate(headlines)])
        prompt = f"""
You are a Senior Wall Street Strategist. Analyze these 5 market headlines:
{headlines_payload}

FOR EACH ARTICLE write an <h3> with the article number and title, then:
- A <p> with a 5-8 sentence deep-dive analysis and potential S&P 500 impact.
- A <p class="vibe"> with label "Vibe Check:" followed by Bullish, Bearish, or Neutral.

After all 5 articles, on its own line output exactly this (replace values):
SENTIMENT_DATA: {{"label": "Bullish", "score": 78}}

Where label is the OVERALL market sentiment (Bullish / Neutral / Bearish) and score is 0-100.
Do not include markdown code fences. Output clean HTML only.
"""
        try:
            gemini = get_model()
            if gemini:
                raw = gemini.generate_content(prompt).text
                sentiment_label, sentiment_score = parse_sentiment(raw)
                ai_analysis = strip_sentiment_line(raw)
            else:
                ai_analysis = "<p>AI Analyst unavailable — no Google Cloud project configured.</p>"
        except Exception as e:
            ai_analysis = f"<p>AI Analysis Failed: {str(e)}</p>"

    # Sentiment display config: user spec — red up = bullish, yellow flat = neutral, green down = bearish
    if sentiment_label == "Bullish":
        sentiment_arrow = "&#8679;"   # ⇑ up arrow
        sentiment_color = "#e53e3e"   # red
        sentiment_bg    = "#fff5f5"
        sentiment_border= "#fc8181"
        sentiment_word  = "Positive"
    elif sentiment_label == "Bearish":
        sentiment_arrow = "&#8681;"   # ⇓ down arrow
        sentiment_color = "#38a169"   # green
        sentiment_bg    = "#f0fff4"
        sentiment_border= "#68d391"
        sentiment_word  = "Negative"
    else:
        sentiment_arrow = "&#8212;"   # — flat line
        sentiment_color = "#d69e2e"   # yellow/gold
        sentiment_bg    = "#fffff0"
        sentiment_border= "#f6e05e"
        sentiment_word  = "Neutral"

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Market News Agent</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #eef1f6;
            color: #2d3748;
            min-height: 100vh;
            padding: 32px 16px;
        }

        .container {
            max-width: 860px;
            margin: 0 auto;
        }

        /* Header */
        header {
            background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
            color: white;
            padding: 28px 32px;
            border-radius: 16px 16px 0 0;
            margin-bottom: 2px;
        }
        header h1 { font-size: 1.6rem; font-weight: 700; letter-spacing: -0.3px; }
        header p  { font-size: 0.9rem; opacity: 0.8; margin-top: 4px; }

        /* Sentiment banner */
        .sentiment-bar {
            background: {{ sentiment_bg }};
            border: 2px solid {{ sentiment_border }};
            border-radius: 0;
            padding: 18px 32px;
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 2px;
        }
        .sentiment-arrow {
            font-size: 3rem;
            color: {{ sentiment_color }};
            line-height: 1;
            font-weight: 900;
        }
        .sentiment-info { flex: 1; }
        .sentiment-label {
            font-size: 1.25rem;
            font-weight: 700;
            color: {{ sentiment_color }};
        }
        .sentiment-sub { font-size: 0.85rem; color: #718096; margin-top: 2px; }
        .sentiment-score {
            font-size: 2rem;
            font-weight: 800;
            color: {{ sentiment_color }};
        }
        .sentiment-score span { font-size: 0.9rem; font-weight: 500; color: #718096; }

        /* Main card */
        .card {
            background: white;
            border-radius: 0 0 16px 16px;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        }

        /* Section label */
        .section-label {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: #a0aec0;
            padding: 20px 28px 10px;
        }

        /* News list */
        .news-list { list-style: none; border-top: 1px solid #edf2f7; }
        .news-list li { border-bottom: 1px solid #edf2f7; }
        .news-list li:last-child { border-bottom: none; }

        .news-link {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px 28px;
            text-decoration: none;
            color: inherit;
            transition: background 0.15s;
        }
        .news-link:hover { background: #f7fafc; }
        .news-link:hover .news-title { color: #2b6cb0; }
        .news-link:hover .news-arrow { opacity: 1; transform: translateX(3px); }

        .news-num {
            flex-shrink: 0;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background: #ebf8ff;
            color: #2b6cb0;
            font-size: 0.75rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .news-title {
            flex: 1;
            font-size: 0.95rem;
            font-weight: 500;
            line-height: 1.4;
            color: #1a202c;
            transition: color 0.15s;
        }
        .news-arrow {
            flex-shrink: 0;
            color: #a0aec0;
            font-size: 1.1rem;
            opacity: 0;
            transition: opacity 0.15s, transform 0.15s;
        }

        /* Analysis accordion */
        .analysis-section { padding: 20px 28px 28px; border-top: 1px solid #edf2f7; }

        details.analysis-block { margin-bottom: 0; }
        details.analysis-block + details.analysis-block { margin-top: 10px; }

        summary.analysis-toggle {
            cursor: pointer;
            list-style: none;
            background: #2b6cb0;
            color: white;
            padding: 13px 18px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            user-select: none;
            transition: background 0.15s;
        }
        summary.analysis-toggle::-webkit-details-marker { display: none; }
        summary.analysis-toggle:hover { background: #1a365d; }
        summary.analysis-toggle::after {
            content: '▼ expand';
            font-size: 0.75rem;
            font-weight: 400;
            opacity: 0.8;
        }
        details[open] summary.analysis-toggle { border-radius: 10px 10px 0 0; }
        details[open] summary.analysis-toggle::after { content: '▲ collapse'; }

        .analysis-body {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-top: none;
            border-radius: 0 0 10px 10px;
            padding: 20px;
        }
        .analysis-body h3 { color: #2c5282; font-size: 1rem; margin-bottom: 10px; }
        .analysis-body p  { font-size: 0.9rem; line-height: 1.7; margin-bottom: 12px; text-align: justify; }
        .analysis-body p:last-child { margin-bottom: 0; }
        .analysis-body .vibe { font-weight: 600; color: #2b6cb0; }

        /* Refresh */
        .refresh-wrap { padding: 0 28px 28px; }
        .refresh-btn {
            width: 100%;
            padding: 12px;
            background: #2b6cb0;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s;
        }
        .refresh-btn:hover { background: #1a365d; }
    </style>
</head>
<body>
<div class="container">

    <header>
        <h1>AI Market News Agent</h1>
        <p>Live headlines + Gemini-powered deep-dive analysis</p>
    </header>

    <!-- Sentiment banner -->
    <div class="sentiment-bar">
        <div class="sentiment-arrow">{{ sentiment_arrow | safe }}</div>
        <div class="sentiment-info">
            <div class="sentiment-label">{{ sentiment_word }} &mdash; {{ sentiment_label }}</div>
            <div class="sentiment-sub">Overall market sentiment based on today's headlines</div>
        </div>
        <div class="sentiment-score">{{ sentiment_score }}<span>&nbsp;/ 100</span></div>
    </div>

    <div class="card">
        <!-- Clickable headlines -->
        <div class="section-label">Today's Top Headlines</div>
        <ul class="news-list">
            {% for article in articles %}
            <li>
                <a class="news-link" href="{{ article.link }}" target="_blank" rel="noopener noreferrer">
                    <span class="news-num">{{ loop.index }}</span>
                    <span class="news-title">{{ article.title }}</span>
                    <span class="news-arrow">&#8594;</span>
                </a>
            </li>
            {% endfor %}
        </ul>

        <!-- Expandable AI analysis -->
        <div class="analysis-section">
            <div class="section-label" style="padding: 0 0 12px 0;">AI Deep-Dive Analysis — click to expand</div>
            <details class="analysis-block">
                <summary class="analysis-toggle">Full Market Analysis</summary>
                <div class="analysis-body">
                    {{ ai_analysis | safe }}
                </div>
            </details>
        </div>

        <!-- Refresh -->
        <div class="refresh-wrap">
            <button class="refresh-btn" onclick="location.reload()">&#8635; Refresh &amp; Re-Analyze</button>
        </div>
    </div>

</div>
</body>
</html>
""",
        articles=articles,
        ai_analysis=ai_analysis,
        sentiment_label=sentiment_label,
        sentiment_score=sentiment_score,
        sentiment_arrow=sentiment_arrow,
        sentiment_color=sentiment_color,
        sentiment_bg=sentiment_bg,
        sentiment_border=sentiment_border,
        sentiment_word=sentiment_word,
    )

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
