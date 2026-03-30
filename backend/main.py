import json
import os
from contextlib import asynccontextmanager

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .database import get_conn, init_db
from .ai_service import analyze_news
from .email_service import send_welcome_email, send_daily_digest
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
                    (title, url, source, summary, analysis_steps, sentiment_label, sentiment_score)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
                """,
                (
                    r["title"],
                    r["url"],
                    r.get("source", ""),
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


@app.post("/api/scheduler/daily")
def scheduler_daily(request: Request):
    """
    Cloud Scheduler webhook — fetches news, stores it, and emails all subscribers.

    This endpoint is the production solution for Cloud Run, where the in-process
    APScheduler cannot be relied on because Cloud Run scales to zero.

    Set up in Google Cloud Scheduler:
      - Schedule:  0 7 * * *  (every day at 07:00)
      - Timezone:  America/Los_Angeles (PST/PDT)
      - URL:       https://your-app.run.app/api/scheduler/daily
      - Method:    POST
      - Auth header: Authorization: Bearer <SCHEDULER_SECRET>

    Set SCHEDULER_SECRET as an environment variable in Cloud Run.
    Leave it unset (or empty) to skip auth — fine for dev/testing.
    """
    # Optional bearer-token auth to prevent unauthorised triggers
    secret = os.environ.get("SCHEDULER_SECRET", "")
    if secret:
        auth = request.headers.get("Authorization", "")
        if auth != f"Bearer {secret}":
            raise HTTPException(status_code=401, detail="Unauthorized")

    print("[Scheduler/daily] Triggered via HTTP — fetching news...")
    try:
        results = analyze_news()
        conn = get_conn()
        cur = conn.cursor()
        for r in results:
            cur.execute(
                """
                INSERT INTO news_items
                    (title, url, source, summary, analysis_steps, sentiment_label, sentiment_score)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
                """,
                (
                    r["title"],
                    r["url"],
                    r.get("source", ""),
                    r["summary"],
                    json.dumps(r["analysis_steps"]),
                    r["sentiment_label"],
                    r["sentiment_score"],
                ),
            )
        conn.commit()
        cur.close()
        conn.close()
        print(f"[Scheduler/daily] Stored {len(results)} items. Sending digest...")
        send_daily_digest(results)
        return {"success": True, "items": len(results)}
    except Exception as e:
        print(f"[Scheduler/daily] Error: {e}")
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


# ── Unsubscribe endpoint ──────────────────────────────────────────────────────

def _html_page(title: str, heading: str, body: str, color: str = "#16a34a") -> HTMLResponse:
    """Return a self-contained HTML page — no React app needed."""
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>{title}</title>
      <style>
        body {{ font-family: Arial, sans-serif; background: #f1f5f9;
                display: flex; align-items: center; justify-content: center;
                min-height: 100vh; margin: 0; }}
        .card {{ background: #fff; border-radius: 12px; padding: 48px 40px;
                 max-width: 480px; width: 90%; text-align: center;
                 box-shadow: 0 4px 24px rgba(0,0,0,.08); }}
        .icon {{ font-size: 56px; margin-bottom: 16px; }}
        h1 {{ color: {color}; font-size: 22px; margin: 0 0 12px; }}
        p  {{ color: #64748b; font-size: 15px; line-height: 1.6; margin: 0; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="icon">{heading}</div>
        {body}
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/api/unsubscribe")
def unsubscribe(email: str = ""):
    """Remove a subscriber by email. Returns a standalone HTML confirmation page."""
    email = email.strip().lower()
    if not email:
        return _html_page(
            "Error", "⚠️",
            "<h1 style='color:#dc2626'>Missing email</h1>"
            "<p>No email address was provided. Please use the unsubscribe link from your confirmation email.</p>",
            color="#dc2626",
        )
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM subscribers WHERE email = %s", (email,))
        deleted = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return _html_page(
            "Error", "⚠️",
            f"<h1 style='color:#dc2626'>Something went wrong</h1><p>{e}</p>",
            color="#dc2626",
        )

    if deleted == 0:
        return _html_page(
            "Not found", "🤔",
            "<h1 style='color:#d97706'>Email not found</h1>"
            f"<p><strong>{email}</strong> is not currently subscribed.</p>",
            color="#d97706",
        )

    return _html_page(
        "Unsubscribed", "✅",
        f"<h1>You're unsubscribed</h1>"
        f"<p><strong>{email}</strong> has been removed.<br/>"
        f"You will no longer receive Market News Daily emails.</p>",
    )


# ── Digest test endpoint ──────────────────────────────────────────────────────

@app.post("/api/digest/send")
def trigger_digest():
    """
    Manually send today's digest to all subscribers right now.
    Useful for testing before the 7 AM scheduler fires.
    Fetches the latest 5 news items from the DB and emails them out.
    """
    try:
        conn = get_conn()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT title, url, source, summary, sentiment_label, sentiment_score "
            "FROM news_items ORDER BY fetched_at DESC LIMIT 5"
        )
        items = [dict(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    if not items:
        raise HTTPException(status_code=404, detail="No news items in database — run Refresh first.")

    try:
        send_daily_digest(items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email error: {e}")

    return {"success": True, "message": f"Digest sent to all subscribers using {len(items)} news items."}


# ── Test email endpoint ───────────────────────────────────────────────────────

class TestEmailRequest(BaseModel):
    email: str

@app.post("/api/email/test")
def send_test_email(req: TestEmailRequest):
    """Send a test welcome email to the given address."""
    try:
        send_welcome_email(req.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email error: {e}")
    return {"success": True, "message": f"Test email sent to {req.email}"}


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
