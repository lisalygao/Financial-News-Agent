import os
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

@app.route("/")
def index():
    articles = get_market_news()
    headlines = [a["title"] for a in articles]

    if not articles:
        ai_analysis = "<p>Agent Error: Could not retrieve live headlines to analyze.</p>"
    else:
        headlines_payload = "\n".join([f"{i+1}. {h}" for i, h in enumerate(headlines)])
        prompt = f"""
        You are a Senior Wall Street Strategist. Analyze these 5 headlines:
        {headlines_payload}

        FOR EACH ARTICLE:
        1. Write a 5-10 sentence deep-dive analysis.
        2. Explain the potential impact on the S&P 500.
        3. Provide a 'Vibe Check' (Bullish/Bearish/Neutral).

        Format the entire response using clean HTML tags (<h3> for titles, <p> for analysis).
        """
        try:
            gemini = get_model()
            if gemini:
                response = gemini.generate_content(prompt)
                ai_analysis = response.text
            else:
                ai_analysis = "<p>AI Analyst unavailable — no Google Cloud project configured.</p>"
        except Exception as e:
            ai_analysis = f"<p>AI Analysis Failed: {str(e)}</p>"

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Financial News Agent</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; line-height: 1.6; padding: 40px; background: #f0f2f5; color: #333; }
            .container { max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
            h1 { color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 10px; margin-bottom: 20px; }
            h2 { color: #2c5282; font-size: 1.1rem; margin-bottom: 12px; }

            /* Headlines list */
            .headlines-list { list-style: none; padding: 0; margin: 0 0 30px 0; }
            .headlines-list li { border-bottom: 1px solid #e2e8f0; padding: 10px 0; }
            .headlines-list li:last-child { border-bottom: none; }
            .headlines-list a {
                color: #2b6cb0;
                text-decoration: none;
                font-weight: 500;
                transition: color 0.2s;
            }
            .headlines-list a:hover { color: #1a365d; text-decoration: underline; }
            .headline-num { color: #a0aec0; font-size: 0.85rem; margin-right: 8px; }

            /* Collapsible AI analysis */
            details { margin-top: 10px; }
            summary {
                cursor: pointer;
                background: #2b6cb0;
                color: white;
                padding: 12px 18px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 1rem;
                list-style: none;
                display: flex;
                align-items: center;
                justify-content: space-between;
                user-select: none;
            }
            summary::-webkit-details-marker { display: none; }
            summary::after { content: '▼ Click to expand'; font-size: 0.8rem; font-weight: 400; }
            details[open] summary::after { content: '▲ Click to collapse'; }
            summary:hover { background: #1a365d; }

            .ai-report { padding: 20px; background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 0 0 8px 8px; }
            .ai-report h3 { color: #2c5282; margin-top: 25px; }
            .ai-report p { margin-bottom: 15px; text-align: justify; }

            /* Refresh button */
            .refresh-btn {
                display: block;
                margin: 30px auto 0;
                padding: 10px 24px;
                background: #3182ce;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                cursor: pointer;
            }
            .refresh-btn:hover { background: #2b6cb0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Expert Market Analysis</h1>

            <h2>Today's Top Headlines</h2>
            <ul class="headlines-list">
                {% for article in articles %}
                <li>
                    <span class="headline-num">{{ loop.index }}.</span>
                    <a href="{{ article.link }}" target="_blank" rel="noopener noreferrer">
                        {{ article.title }}
                    </a>
                </li>
                {% endfor %}
            </ul>

            <details>
                <summary>AI Analyst Deep-Dive</summary>
                <div class="ai-report">
                    {{ ai_analysis | safe }}
                </div>
            </details>

            <button class="refresh-btn" onclick="location.reload()">Refresh News &amp; Re-Analyze</button>
        </div>
    </body>
    </html>
    """, articles=articles, ai_analysis=ai_analysis)

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
