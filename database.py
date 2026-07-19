"""
Database helper for the News Scraper.
Handles creating the SQLite DB, saving articles, and skipping duplicates.
"""

import sqlite3

DB_NAME = "articles.db"


def init_db(db_name: str = DB_NAME):
    """Create the articles table if it doesn't exist yet, and migrate
    older databases (from before multi-source support) to add the
    'source' column if it's missing."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT,
            link TEXT NOT NULL UNIQUE,
            source TEXT DEFAULT 'BBC News',
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migration: if this is an OLD database created before multi-source
    # support, the 'source' column won't exist yet. Add it safely.
    cursor.execute("PRAGMA table_info(articles)")
    columns = [row[1] for row in cursor.fetchall()]
    if "source" not in columns:
        cursor.execute("ALTER TABLE articles ADD COLUMN source TEXT DEFAULT 'BBC News'")
    conn.commit()
    conn.close()


def save_articles(articles: list[dict], db_name: str = DB_NAME) -> list[dict]:
    """
    Insert articles into the DB, skipping ones whose link already exists.
    Returns the list of articles that were ACTUALLY newly inserted
    (so callers can e.g. check them against keyword alerts).
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    newly_inserted = []
    for article in articles:
        try:
            cursor.execute(
                "INSERT INTO articles (title, date, link, source) VALUES (?, ?, ?, ?)",
                (article["title"], article["date"], article["link"], article.get("source", "Unknown")),
            )
            newly_inserted.append(article)
        except sqlite3.IntegrityError:
            # link already exists (UNIQUE constraint) -> skip silently
            continue

    conn.commit()
    conn.close()
    return newly_inserted


def get_all_articles(db_name: str = DB_NAME) -> list[dict]:
    """Fetch every stored article, most recent first."""
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def count_articles(db_name: str = DB_NAME) -> int:
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM articles")
    total = cursor.fetchone()[0]
    conn.close()
    return total


def search_articles(keyword: str = "", source: str = "", db_name: str = DB_NAME) -> list[dict]:
    """Search articles by keyword (in title) and/or filter by source.
    Pass empty strings to skip a filter."""
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM articles WHERE 1=1"
    params = []
    if keyword:
        query += " AND title LIKE ?"
        params.append(f"%{keyword}%")
    if source:
        query += " AND source = ?"
        params.append(source)
    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_sources(db_name: str = DB_NAME) -> list[str]:
    """Return the distinct list of sources currently stored."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT source FROM articles ORDER BY source")
    sources = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sources


def get_source_counts(db_name: str = DB_NAME) -> list[tuple]:
    """Return [(source_name, count), ...] sorted by count descending.
    Used for the 'articles per source' chart."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT source, COUNT(*) as cnt
        FROM articles
        GROUP BY source
        ORDER BY cnt DESC
    """)
    result = cursor.fetchall()
    conn.close()
    return result


def get_daily_counts(days: int = 7, db_name: str = DB_NAME) -> list[tuple]:
    """Return [(date, count), ...] for the last N days, based on when
    each article was scraped. Used for the 'articles per day' chart."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(scraped_at) as day, COUNT(*) as cnt
        FROM articles
        WHERE DATE(scraped_at) >= DATE('now', ?)
        GROUP BY day
        ORDER BY day ASC
    """, (f"-{days} days",))
    result = cursor.fetchall()
    conn.close()
    return result
