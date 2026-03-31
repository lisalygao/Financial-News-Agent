import os
import urllib.parse
import psycopg2
import psycopg2.extras


def get_conn():
    """
    Return a psycopg2 connection, handling both direct TCP and Cloud SQL
    Unix-socket connections automatically.

    Cloud Run + Cloud SQL (recommended GCP setup)
    ---------------------------------------------
    Set INSTANCE_CONNECTION_NAME  = project:region:instance
    Set DATABASE_URL              = postgresql://USER:PASSWORD@/DBNAME
                                    (note: no hostname — just a leading slash)
    The code will automatically route through the Cloud SQL Unix socket at
    /cloudsql/<INSTANCE_CONNECTION_NAME>.

    External PostgreSQL (Neon, Supabase, Railway, etc.)
    ----------------------------------------------------
    Set DATABASE_URL = postgresql://USER:PASSWORD@HOST:PORT/DBNAME
    Leave INSTANCE_CONNECTION_NAME unset.
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Add it in Cloud Run → Edit & Deploy New Revision → Variables & Secrets."
        )

    instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

    # Cloud SQL path: if INSTANCE_CONNECTION_NAME is present and the DATABASE_URL
    # does not already include a cloudsql socket path, connect via Unix socket.
    if instance_connection_name and "/cloudsql/" not in db_url:
        parsed = urllib.parse.urlparse(db_url)
        dbname   = parsed.path.lstrip("/") or "postgres"   # default db if not in URL
        user     = parsed.username or "postgres"
        password = urllib.parse.unquote(parsed.password) if parsed.password else ""
        socket_dir = f"/cloudsql/{instance_connection_name}"
        print(f"[DB] Connecting via Cloud SQL socket: {socket_dir}")
        return psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=socket_dir,
        )

    # Standard TCP path (external DB or already-formatted socket URL)
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
