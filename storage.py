import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs_history.db")

def init_db():
    """Initializes the SQLite database table for sent jobs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_url TEXT UNIQUE,
            title TEXT,
            company TEXT,
            location TEXT,
            source TEXT,
            date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_job_sent(job_url: str) -> bool:
    """Checks whether a job URL has already been alerted to Telegram."""
    if not job_url:
        return True
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sent_jobs WHERE job_url = ?", (job_url.strip(),))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def mark_job_sent(job_url: str, title: str, company: str, location: str, source: str = "LinkedIn"):
    """Records a job as sent so it won't be sent again."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO sent_jobs (job_url, title, company, location, source, date_sent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (job_url.strip(), title, company, location, source, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error recording sent job: {e}")

def get_stats():
    """Returns the count of tracked jobs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sent_jobs")
    total = cursor.fetchone()[0]
    conn.close()
    return total
