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
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized.")
