import json
import os
from contextlib import asynccontextmanager

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .database import get_conn, init_db
from .ai_service import analyze_news
from .email_service import send_welcome_email
from .scheduler import start_scheduler, stop_scheduler


# ── Startup / shutdown ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as exc:
        # Don't crash on startup if DATABASE_URL is missing or unreachable.
        # Cloud Run health checks will pass; individual endpoints return HTTP 500
        # until the variable is configured in the Cloud Run service settings.
        print(f"WARNING: Database initialization skipped — {exc}")
    try:
        start_scheduler()
    except Exception as exc:
        print(f"WARNING: Scheduler failed to start — {exc}")
    yield
    stop_scheduler()   # graceful shutdown — called on SIGTERM (Cloud Run)


app = FastAPI(title="Market News API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ───────────────────────────────────────────────────────────

class SubscribeRequest(BaseModel):
    first_name: str
    last_name: str
    email: str


# ── News endpoints ────────────────────────────────────────────────────────────

@app.get("/api/news")
def get_news():
    """Return the 5 most recently fetched news items."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT * FROM news_items ORDER BY fetched_at DESC LIMIT 5"
    )
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {"items": rows}


@app.post("/api/news/refresh")
def refresh_news():
    """Fetch fresh news, analyse it, and store in the database."""
    try:
        results = analyze_news()
        conn = get_conn()
        cur = conn.cursor()
        for r in results:
            cur.execute(
                """
                INSERT INTO news_items
                    (title, url, summary, analysis_steps, sentiment_label, sentiment_score)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                """,
                (
                    r["title"],
                    r["url"],
                    r["summary"],
                    json.dumps(r["analysis_steps"]),
                    r["sentiment_label"],
                    r["sentiment_score"],
                ),
            )
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Subscribe endpoint ────────────────────────────────────────────────────────

@app.post("/api/subscribe")
def subscribe(body: SubscribeRequest):
    first = body.first_name.strip()
    last  = body.last_name.strip()
    email = body.email.strip().lower()

    if not first or not last or not email:
        raise HTTPException(status_code=400, detail="All fields are required.")
    if "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Invalid email address.")

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO subscribers (first_name, last_name, email) VALUES (%s, %s, %s)",
            (first, last, email),
        )
        conn.commit()
        cur.close()
        conn.close()
        send_welcome_email(email)
        return {"success": True, "message": f"Welcome, {first}! You're subscribed."}
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="This email is already subscribed.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Archive endpoint ──────────────────────────────────────────────────────────

@app.get("/api/archive")
def get_archive():
    """Return all stored news items ordered by most recent first."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM news_items ORDER BY fetched_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {"items": rows}


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


# ── Serve React in production (Docker) ───────────────────────────────────────
# Look for 'static' folder which we created in the Dockerfile
# instead of reaching back into '../frontend/dist'
DIST = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(DIST):
    # Serve the assets (JS/CSS)
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")), name="assets")

    # Catch-all route to serve index.html for the React SPA
    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        index_path = os.path.join(DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend build not found"}
else:
    # If the folder is missing, don't crash, just log it
    print(f"WARNING: Static directory not found at {DIST}")
