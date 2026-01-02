import sqlite3
import time

from constants import *


def init():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS app_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app TEXT NOT NULL,
            start_ts REAL NOT NULL,
            end_ts REAL
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_app_sessions_app
        ON app_sessions(app)
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_app_sessions_start
        ON app_sessions(start_ts)
    """)

    # Improve concurrent read/write behavior
    cur.execute("PRAGMA journal_mode=WAL;")

    conn.commit()
    conn.close()

    _repair_open_sessions()


def start_session(app, start_ts):
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO app_sessions (app, start_ts) VALUES (?, ?)",
        (app, start_ts),
    )

    session_id = cur.lastrowid
    conn.commit()
    conn.close()

    return session_id


def end_session(session_id, end_ts):
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        "UPDATE app_sessions SET end_ts = ? WHERE id = ?",
        (end_ts, session_id),
    )

    conn.commit()
    conn.close()


def close():
    # SQLite connections are short-lived here; nothing persistent to close
    pass


def _repair_open_sessions():
    """
    Close any session left open due to crash or forced shutdown.
    Uses startup time as a conservative end timestamp.
    """
    now = time.time()
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        "UPDATE app_sessions SET end_ts = ? WHERE end_ts IS NULL",
        (now,),
    )

    conn.commit()
    conn.close()


def _get_conn():
    return sqlite3.connect(DB_PATH)


def get_last_sessions(limit):
    """
    Returns the most recent sessions, ordered by start time descending.
    """
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, app, start_ts, end_ts
        FROM app_sessions
        ORDER BY start_ts DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def get_sessions_by_date(date_str):
    """
    date_str format: YYYY-MM-DD
    Returns all sessions whose start_ts falls on that date.
    """
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, app, start_ts, end_ts
        FROM app_sessions
        WHERE DATE(start_ts, 'unixepoch') = ?
        ORDER BY start_ts
        """,
        (date_str,),
    )

    rows = cur.fetchall()
    conn.close()
    return rows


def get_total_duration_for_date(date_str):
    """
    Returns total duration in seconds for a given date.
    Sessions without end_ts are ignored.
    """
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT SUM(end_ts - start_ts)
        FROM app_sessions
        WHERE
            end_ts IS NOT NULL
            AND DATE(start_ts, 'unixepoch') = ?
        """,
        (date_str,),
    )

    result = cur.fetchone()[0]
    conn.close()
    return result or 0
