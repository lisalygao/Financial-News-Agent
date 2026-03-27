# AI Market News Agent

A financial news dashboard with AI-powered analysis, built with FastAPI (Python) and React (Tailwind CSS). Designed for GitHub export and Vertex AI deployment.

## Architecture

```
backend/          FastAPI Python API
  main.py         Routes: /api/news, /api/subscribe, /api/archive, /api/health
  database.py     PostgreSQL helpers (init + connection)
  ai_service.py   RSS fetch + AI placeholder functions (wire to Vertex AI Gemini here)
  scheduler.py    APScheduler — daily fetch at 7:00 AM PST
  requirements.txt

frontend/         React + Vite + Tailwind CSS
  src/
    pages/        NewsPage, SubscribePage, ArchivePage
    components/   Header, NewsCard, SentimentMeter, StepAnalysis
  vite.config.js  Dev proxy: /api/* → localhost:8000

Dockerfile        Multi-stage: builds React, layers with FastAPI. Runs on PORT 8080.
```

## Local Development (Replit)

Two workflows run in parallel:
- **Backend API** — `uvicorn backend.main:app --reload --port 8000` (console)
- **Start application** — `cd frontend && npm run dev` (webview on port 5000)

The Vite dev server proxies all `/api/*` requests to the FastAPI backend at port 8000.

## Database

PostgreSQL via `DATABASE_URL` environment variable.

Tables:
- `subscribers` — id, first_name, last_name, email, subscribed_at
- `news_items` — id, title, url, summary, analysis_steps (JSONB), sentiment_label, sentiment_score, fetched_at

## AI Integration

All AI functions live in `backend/ai_service.py`. Each placeholder function contains the exact Vertex AI Gemini code to drop in as a TODO comment:
- `ai_generate_summary(headline)` — 2-3 sentence summary
- `ai_generate_analysis_steps(headline)` — 5-step reasoning list
- `ai_get_sentiment(headline)` — `{"label": "Bullish|Neutral|Bearish", "score": 0-100}`

## Sentiment Color Spec (user-defined)

| Label   | Arrow | Color  |
|---------|-------|--------|
| Bullish | ↑     | Red    |
| Neutral | —     | Yellow |
| Bearish | ↓     | Green  |

## Deployment (Vertex AI)

```bash
docker build -t market-news .
docker run -e DATABASE_URL=... -e PORT=8080 -p 8080:8080 market-news
```

The Docker image compiles the React frontend (Stage 1) and serves it as static files via FastAPI (Stage 2). FastAPI handles both the SPA and all API routes.

## Key Dependencies

**Python:** fastapi, uvicorn, psycopg2-binary, apscheduler, pytz, requests, beautifulsoup4

**Node:** react, react-router-dom, axios, vite, tailwindcss (v4), @tailwindcss/postcss
