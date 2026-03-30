import os
import psycopg2
import psycopg2.extras


def get_conn():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Add it in your Cloud Run service → Edit & Deploy New Revision "
            "→ Variables & Secrets."
        )
    return psycopg2.connect(db_url)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id            SERIAL PRIMARY KEY,
            first_name    VARCHAR(100) NOT NULL,
            last_name     VARCHAR(100) NOT NULL,
            email         VARCHAR(255) UNIQUE NOT NULL,
            subscribed_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news_items (
            id              SERIAL PRIMARY KEY,
            title           TEXT NOT NULL,
            url             TEXT NOT NULL,
            summary         TEXT,
            analysis_steps  JSONB DEFAULT '[]'::jsonb,
            sentiment_label VARCHAR(20),
            sentiment_score INTEGER,
            fetched_at      TIMESTAMP DEFAULT NOW()
        )
    """)
    # Add source column if it doesn't exist yet (safe migration)
    cur.execute("""
        ALTER TABLE news_items
        ADD COLUMN IF NOT EXISTS source TEXT DEFAULT ''
    """)
    # One-time cleanup: fix any URLs that are missing the domain prefix.
    # Old records stored only the raw Google News base64 ID (e.g. "CBMi9gFB...")
    # instead of a full URL. Prepending the Google News base URL makes them
    # clickable in a browser (Google redirects to the original article).
    cur.execute("""
        UPDATE news_items
        SET url = 'https://news.google.com/rss/articles/' || url
        WHERE url NOT LIKE 'http%'
          AND url <> ''
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized.")
