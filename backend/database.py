import os
import psycopg2
import psycopg2.extras


def get_conn():
    # If running on Cloud Run, use the Unix socket
    if os.environ.get("K_SERVICE"): 
        # Replace these with your actual DB credentials
        return psycopg2.connect(
            database="market_news",
            user="postgres",
            password="your-password",
            host=f"/cloudsql/{os.environ.get('CLOUD_SQL_CONNECTION_NAME')}"
        )
    # Otherwise, use local/Replit settings
    return psycopg2.connect(os.environ.get("DATABASE_URL"))


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
