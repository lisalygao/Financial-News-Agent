import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# Fallback Project ID
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "my-first-app-491201")
vertexai.init(project=PROJECT_ID, location="us-central1")
model = GenerativeModel("gemini-1.5-flash-002")

def get_market_news():
    try:
        rss_url = "https://news.google.com/rss/search?q=stock+market+analysis&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(rss_url, timeout=10)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item", limit=5)
        return [item.title.text for item in items]
    except Exception as e:
        print(f"Scraping Error: {e}")
        return []

@app.route("/")
def index():
    headlines = get_market_news()

    if not headlines:
        ai_analysis = "Agent Error: Could not retrieve live headlines to analyze."
    else:
        # Create a clearly numbered list for the AI to read
        headlines_payload = "\n".join([f"{i+1}. {h}" for i, h in enumerate(headlines)])

        # THE "EXPERT" PROMPT
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
            response = model.generate_content(prompt)
            ai_analysis = response.text
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
            h1 { color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 10px; }
            .ai-report { margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 20px; }
            h3 { color: #2c5282; margin-top: 25px; }
            p { margin-bottom: 15px; text-align: justify; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Expert Market Analysis</h1>
            <div class="ai-report">
                {{ ai_analysis | safe }}
            </div>
            <p style="text-align:center; margin-top:40px;">
                <button onclick="location.reload()" style="padding:10px 20px; cursor:pointer;">Refresh News & Re-Analyze</button>
            </p>
        </div>
    </body>
    </html>
    """, ai_analysis=ai_analysis)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)