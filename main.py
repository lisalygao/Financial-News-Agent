import os
from flask import Flask, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

# 1. Initialize Vertex AI 
# (Cloud Run automatically handles the 'credentials' part for you!)
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT") # This picks up your Project ID
LOCATION = "us-central1" # Or your preferred region
vertexai.init(project=PROJECT_ID, location=LOCATION)

# 2. Load the Gemini Model
model = GenerativeModel("gemini-1.5-flash")

@app.route("/")
def index():
    # Let's ask Gemini for a "Market Vibe" check
    try:
        response = model.generate_content("Give me a 1-sentence witty forecast for the tech stock market today.")
        market_vibe = response.text
    except Exception as e:
        market_vibe = f"AI is resting... (Error: {str(e)})"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Financial News Agent</title>
        <style>
            body {{ font-family: sans-serif; background: #f0f4f8; display: flex; align-items: center; justify-content: center; min-height: 100vh; }}
            .card {{ background: white; border-radius: 12px; padding: 40px; box-shadow: 0 4px 24px rgba(0,0,0,0.1); text-align: center; max-width: 500px; }}
            h1 {{ color: #1a202c; }}
            .vibe {{ font-style: italic; color: #2b6cb0; margin-top: 20px; border-left: 4px solid #2b6cb0; padding-left: 15px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Financial News Agent</h1>
            <p><strong>Today's AI Analysis:</strong></p>
            <div class="vibe">{market_vibe}</div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)