import os
import re
import json
import requests
import psycopg2
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel

app = Flask(__name__)

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "my-first-app-491201")
model = None

# ── Database ──────────────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                id            SERIAL PRIMARY KEY,
                first_name    VARCHAR(100) NOT NULL,
                last_name     VARCHAR(100) NOT NULL,
                email         VARCHAR(255) NOT NULL UNIQUE,
                subscribed_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB init error: {e}")

init_db()

# ── Gemini ────────────────────────────────────────────────────────────────────

def get_model():
    global model
    if model is None and PROJECT_ID:
        vertexai.init(project=PROJECT_ID, location="us-central1")
        model = GenerativeModel("gemini-2.5-flash")
    return model

# ── News ──────────────────────────────────────────────────────────────────────

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
    match = re.search(r'SENTIMENT_DATA:\s*(\{.*?\})', raw_text)
    if match:
        try:
            data = json.loads(match.group(1))
            return data.get("label", "Neutral"), int(data.get("score", 50))
        except Exception:
            pass
    return "Neutral", 50

def strip_sentiment_line(raw_text):
    return re.sub(r'SENTIMENT_DATA:\s*\{.*?\}\n?', '', raw_text).strip()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    first_name = (data.get("first_name") or "").strip()
    last_name  = (data.get("last_name")  or "").strip()
    email      = (data.get("email")      or "").strip().lower()

    if not first_name or not last_name or not email:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    if "@" not in email or "." not in email:
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO subscribers (first_name, last_name, email) VALUES (%s, %s, %s)",
            (first_name, last_name, email)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": f"Welcome, {first_name}! You're now subscribed."})
    except psycopg2.errors.UniqueViolation:
        return jsonify({"success": False, "message": "This email is already subscribed."}), 409
    except Exception as e:
        print(f"Subscribe error: {e}")
        return jsonify({"success": False, "message": "Something went wrong. Please try again."}), 500

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

    if sentiment_label == "Bullish":
        sentiment_arrow = "&#8679;"
        sentiment_color = "#e53e3e"
        sentiment_bg    = "#fff5f5"
        sentiment_border= "#fc8181"
        sentiment_word  = "Positive"
    elif sentiment_label == "Bearish":
        sentiment_arrow = "&#8681;"
        sentiment_color = "#38a169"
        sentiment_bg    = "#f0fff4"
        sentiment_border= "#68d391"
        sentiment_word  = "Negative"
    else:
        sentiment_arrow = "&#8212;"
        sentiment_color = "#d69e2e"
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
        .container { max-width: 860px; margin: 0 auto; }

        /* ── Header ── */
        header {
            background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
            color: white;
            padding: 24px 32px;
            border-radius: 16px 16px 0 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 2px;
        }
        .header-text h1 { font-size: 1.5rem; font-weight: 700; }
        .header-text p  { font-size: 0.85rem; opacity: 0.8; margin-top: 3px; }

        .subscribe-btn {
            flex-shrink: 0;
            background: white;
            color: #2b6cb0;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 0.9rem;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.15s, color 0.15s;
            white-space: nowrap;
        }
        .subscribe-btn:hover { background: #ebf8ff; }

        /* ── Sentiment banner ── */
        .sentiment-bar {
            background: {{ sentiment_bg }};
            border: 2px solid {{ sentiment_border }};
            padding: 18px 32px;
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 2px;
        }
        .sentiment-arrow { font-size: 3rem; color: {{ sentiment_color }}; font-weight: 900; line-height: 1; }
        .sentiment-info { flex: 1; }
        .sentiment-label { font-size: 1.2rem; font-weight: 700; color: {{ sentiment_color }}; }
        .sentiment-sub   { font-size: 0.82rem; color: #718096; margin-top: 2px; }
        .sentiment-score { font-size: 2rem; font-weight: 800; color: {{ sentiment_color }}; }
        .sentiment-score span { font-size: 0.85rem; font-weight: 500; color: #718096; }

        /* ── Card ── */
        .card {
            background: white;
            border-radius: 0 0 16px 16px;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        }
        .section-label {
            font-size: 0.68rem; font-weight: 700; letter-spacing: 1.2px;
            text-transform: uppercase; color: #a0aec0; padding: 20px 28px 10px;
        }

        /* ── News list ── */
        .news-list { list-style: none; border-top: 1px solid #edf2f7; }
        .news-list li { border-bottom: 1px solid #edf2f7; }
        .news-list li:last-child { border-bottom: none; }
        .news-link {
            display: flex; align-items: center; gap: 16px;
            padding: 16px 28px; text-decoration: none; color: inherit;
            transition: background 0.15s;
        }
        .news-link:hover { background: #f7fafc; }
        .news-link:hover .news-title { color: #2b6cb0; }
        .news-link:hover .news-arrow { opacity: 1; transform: translateX(3px); }
        .news-num {
            flex-shrink: 0; width: 26px; height: 26px; border-radius: 50%;
            background: #ebf8ff; color: #2b6cb0; font-size: 0.75rem;
            font-weight: 700; display: flex; align-items: center; justify-content: center;
        }
        .news-title {
            flex: 1; font-size: 0.95rem; font-weight: 500; line-height: 1.4;
            color: #1a202c; transition: color 0.15s;
        }
        .news-arrow {
            flex-shrink: 0; color: #a0aec0; font-size: 1.1rem;
            opacity: 0; transition: opacity 0.15s, transform 0.15s;
        }

        /* ── Analysis accordion ── */
        .analysis-section { padding: 20px 28px 28px; border-top: 1px solid #edf2f7; }
        summary.analysis-toggle {
            cursor: pointer; list-style: none; background: #2b6cb0; color: white;
            padding: 13px 18px; border-radius: 10px; font-weight: 600; font-size: 0.95rem;
            display: flex; align-items: center; justify-content: space-between;
            user-select: none; transition: background 0.15s;
        }
        summary.analysis-toggle::-webkit-details-marker { display: none; }
        summary.analysis-toggle:hover { background: #1a365d; }
        summary.analysis-toggle::after { content: '▼ expand'; font-size: 0.75rem; font-weight: 400; opacity: 0.8; }
        details[open] summary.analysis-toggle { border-radius: 10px 10px 0 0; }
        details[open] summary.analysis-toggle::after { content: '▲ collapse'; }
        .analysis-body {
            background: #f7fafc; border: 1px solid #e2e8f0; border-top: none;
            border-radius: 0 0 10px 10px; padding: 20px;
        }
        .analysis-body h3  { color: #2c5282; font-size: 1rem; margin-bottom: 10px; }
        .analysis-body p   { font-size: 0.9rem; line-height: 1.7; margin-bottom: 12px; text-align: justify; }
        .analysis-body p:last-child { margin-bottom: 0; }
        .analysis-body .vibe { font-weight: 600; color: #2b6cb0; }

        /* ── Refresh ── */
        .refresh-wrap { padding: 0 28px 28px; }
        .refresh-btn {
            width: 100%; padding: 12px; background: #2b6cb0; color: white;
            border: none; border-radius: 10px; font-size: 0.95rem; font-weight: 600;
            cursor: pointer; transition: background 0.15s;
        }
        .refresh-btn:hover { background: #1a365d; }

        /* ── Modal overlay ── */
        .modal-overlay {
            display: none; position: fixed; inset: 0;
            background: rgba(0,0,0,0.55); z-index: 100;
            align-items: center; justify-content: center;
        }
        .modal-overlay.open { display: flex; }

        .modal {
            background: white; border-radius: 16px; padding: 36px 32px;
            width: 100%; max-width: 420px; box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            position: relative;
        }
        .modal h2 { font-size: 1.3rem; color: #1a365d; margin-bottom: 6px; }
        .modal p.sub { font-size: 0.85rem; color: #718096; margin-bottom: 24px; }

        .modal-close {
            position: absolute; top: 16px; right: 18px;
            background: none; border: none; font-size: 1.4rem;
            color: #a0aec0; cursor: pointer; line-height: 1;
        }
        .modal-close:hover { color: #2d3748; }

        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 0.82rem; font-weight: 600; color: #4a5568; margin-bottom: 5px; }
        .form-group input {
            width: 100%; padding: 10px 14px; border: 1.5px solid #e2e8f0;
            border-radius: 8px; font-size: 0.95rem; color: #2d3748;
            transition: border-color 0.15s; outline: none;
        }
        .form-group input:focus { border-color: #2b6cb0; }

        .submit-btn {
            width: 100%; padding: 12px; background: #2b6cb0; color: white;
            border: none; border-radius: 8px; font-size: 1rem; font-weight: 700;
            cursor: pointer; transition: background 0.15s; margin-top: 6px;
        }
        .submit-btn:hover { background: #1a365d; }
        .submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

        .form-message {
            margin-top: 14px; padding: 10px 14px; border-radius: 8px;
            font-size: 0.87rem; font-weight: 500; display: none;
        }
        .form-message.success { background: #f0fff4; color: #276749; border: 1px solid #9ae6b4; }
        .form-message.error   { background: #fff5f5; color: #c53030; border: 1px solid #feb2b2; }
    </style>
</head>
<body>
<div class="container">

    <header>
        <div class="header-text">
            <h1>AI Market News Agent</h1>
            <p>Live headlines + Gemini-powered deep-dive analysis</p>
        </div>
        <button class="subscribe-btn" onclick="openModal()">&#9993; Subscribe</button>
    </header>

    <div class="sentiment-bar">
        <div class="sentiment-arrow">{{ sentiment_arrow | safe }}</div>
        <div class="sentiment-info">
            <div class="sentiment-label">{{ sentiment_word }} &mdash; {{ sentiment_label }}</div>
            <div class="sentiment-sub">Overall market sentiment based on today's headlines</div>
        </div>
        <div class="sentiment-score">{{ sentiment_score }}<span>&nbsp;/ 100</span></div>
    </div>

    <div class="card">
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

        <div class="analysis-section">
            <div class="section-label" style="padding:0 0 12px 0;">AI Deep-Dive Analysis — click to expand</div>
            <details class="analysis-block">
                <summary class="analysis-toggle">Full Market Analysis</summary>
                <div class="analysis-body">{{ ai_analysis | safe }}</div>
            </details>
        </div>

        <div class="refresh-wrap">
            <button class="refresh-btn" onclick="location.reload()">&#8635; Refresh &amp; Re-Analyze</button>
        </div>
    </div>
</div>

<!-- Subscribe modal -->
<div class="modal-overlay" id="modalOverlay" onclick="handleOverlayClick(event)">
    <div class="modal">
        <button class="modal-close" onclick="closeModal()" aria-label="Close">&times;</button>
        <h2>&#128276; Stay Informed</h2>
        <p class="sub">Get the latest market analysis delivered to your inbox.</p>

        <form id="subscribeForm" onsubmit="handleSubmit(event)">
            <div class="form-group">
                <label for="firstName">First Name</label>
                <input type="text" id="firstName" placeholder="Jane" required>
            </div>
            <div class="form-group">
                <label for="lastName">Last Name</label>
                <input type="text" id="lastName" placeholder="Doe" required>
            </div>
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" placeholder="jane@example.com" required>
            </div>
            <button type="submit" class="submit-btn" id="submitBtn">Subscribe Now</button>
        </form>

        <div class="form-message" id="formMessage"></div>
    </div>
</div>

<script>
    function openModal() {
        document.getElementById('modalOverlay').classList.add('open');
        document.getElementById('firstName').focus();
    }
    function closeModal() {
        document.getElementById('modalOverlay').classList.remove('open');
        document.getElementById('formMessage').style.display = 'none';
        document.getElementById('formMessage').className = 'form-message';
        document.getElementById('subscribeForm').reset();
        document.getElementById('submitBtn').disabled = false;
        document.getElementById('submitBtn').textContent = 'Subscribe Now';
    }
    function handleOverlayClick(e) {
        if (e.target === document.getElementById('modalOverlay')) closeModal();
    }
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeModal();
    });

    async function handleSubmit(e) {
        e.preventDefault();
        const btn = document.getElementById('submitBtn');
        const msg = document.getElementById('formMessage');
        btn.disabled = true;
        btn.textContent = 'Submitting...';
        msg.style.display = 'none';

        const payload = {
            first_name: document.getElementById('firstName').value.trim(),
            last_name:  document.getElementById('lastName').value.trim(),
            email:      document.getElementById('email').value.trim()
        };

        try {
            const res  = await fetch('/subscribe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            msg.textContent  = data.message;
            msg.className    = 'form-message ' + (data.success ? 'success' : 'error');
            msg.style.display = 'block';

            if (data.success) {
                document.getElementById('subscribeForm').reset();
                btn.textContent = '&#10003; Subscribed!';
            } else {
                btn.disabled    = false;
                btn.textContent = 'Subscribe Now';
            }
        } catch (err) {
            msg.textContent   = 'Network error. Please try again.';
            msg.className     = 'form-message error';
            msg.style.display = 'block';
            btn.disabled      = false;
            btn.textContent   = 'Subscribe Now';
        }
    }
</script>
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
