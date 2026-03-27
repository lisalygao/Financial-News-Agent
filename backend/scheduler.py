"""
Background scheduler — triggers news fetch every day at 7:00 AM PST.
Uses APScheduler with the America/Los_Angeles timezone.
"""

import json
import psycopg2
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from .ai_service import analyze_news
from .database import get_conn

_scheduler = BackgroundScheduler()


def _fetch_and_store():
    """Fetch fresh news and insert into the database."""
    print("[Scheduler] Running daily news fetch...")
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
        print(f"[Scheduler] Stored {len(results)} news items.")
    except Exception as e:
        print(f"[Scheduler] Error: {e}")


def start_scheduler():
    if not _scheduler.running:
        pst = pytz.timezone("America/Los_Angeles")
        _scheduler.add_job(
            _fetch_and_store,
            CronTrigger(hour=7, minute=0, timezone=pst),
            id="daily_news_fetch",
            replace_existing=True,
        )
        _scheduler.start()
        print("[Scheduler] Started — daily fetch at 07:00 PST.")
