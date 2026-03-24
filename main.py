import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# Initialize Vertex AI
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
vertexai.init(project=PROJECT_ID, location="us-central1")
model = GenerativeModel("gemini-1.5-flash")

def get_market_news():
    """Fetches the top 5 finance headlines from Google News RSS."""
    rss_url = "https://news.google.com/rss/search?q=stock+market+analysis&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item", limit=5)
    return [item.title.text for item in items]

@app.route("/")
def index():
    headlines = get_market_news()
    headlines_str = "\n".join([f"- {h}" in headlines])

    # The Prompt for Gemini
    prompt = f"""
    You are a professional financial analyst. Based on these headlines:
    {headlines_str}

    Provide a 2-sentence market summary and a 'Vibe Check' (Bullish, Bearish, or Neutral).
    Format the output as clean HTML.
    """

    try:
        ai_response = model.generate_content(prompt).text
    except Exception as e:
        ai_response = f"<p>AI Analyst is offline: {str(e)}</p>"

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Market News Agent</title>
        <style>
            body { font-family: sans-serif; line-height: 1.6; padding: 40px; background: #f4f7f6; }
            .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .headlines { font-size: 0.9rem; color: #7f8c8d; margin-bottom: 20px; }
            .ai-analysis { background: #e8f4fd; padding: 15px; border-left: 5px solid #3498db; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Market News Agent</h1>
            <h3>Today's Headlines:</h3>
            <div class="headlines">
                <ul>
                    {% for h in headlines %}
                        <li>{{ h }}</li>
                    {% endfor %}
                </ul>
            </div>
            <h3>AI Analyst Vibe:</h3>
            <div class="ai-analysis">
                {{ ai_analysis | safe }}
            </div>
        </div>
    </body>
    </html>
    """, headlines=headlines, ai_analysis=ai_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)