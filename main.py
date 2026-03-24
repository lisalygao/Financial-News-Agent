import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>My App</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f0f4f8;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 48px 40px;
                max-width: 480px;
                width: 90%;
                box-shadow: 0 4px 24px rgba(0,0,0,0.08);
                text-align: center;
            }
            h1 { font-size: 2rem; color: #1a202c; margin-bottom: 12px; }
            p { color: #4a5568; font-size: 1.05rem; line-height: 1.6; margin-bottom: 24px; }
            .badge {
                display: inline-block;
                background: #ebf8ff;
                color: #2b6cb0;
                border-radius: 20px;
                padding: 6px 18px;
                font-size: 0.85rem;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Hello, World!</h1>
            <p>Your Flask app is up and running. Ready for Vertex AI deployment.</p>
            <span class="badge">Deployed with Docker</span>
        </div>
    </body>
    </html>
    """

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
