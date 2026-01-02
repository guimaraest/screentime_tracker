import sqlite3
import time
import threading

from constants import *


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False,
        )
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA busy_timeout = 3000;")
        self.db_lock = threading.Lock()

        self._setup_schema()
        self._repair_open_sessions()

    def _setup_schema(self):
        with self.db_lock:
            cur = self.conn.cursor()

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

            self.conn.commit()

    def _repair_open_sessions(self):
        now = time.time()
        with self.db_lock:
            self.conn.execute(
                "UPDATE app_sessions SET end_ts = ? WHERE end_ts IS NULL",
                (now,),
            )
            self.conn.commit()

    def start_session(self, app, start_ts):
        with self.db_lock:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO app_sessions (app, start_ts) VALUES (?, ?)",
                (app, start_ts),
            )
            self.conn.commit()
            return cur.lastrowid

    def end_session(self, session_id, end_ts):
        with self.db_lock:
            self.conn.execute(
                "UPDATE app_sessions SET end_ts = ? WHERE id = ?",
                (end_ts, session_id),
            )
            self.conn.commit()

    def get_last_sessions(self, limit):
        with self.db_lock:
            cur = self.conn.cursor()
            cur.execute(
                """
                SELECT id, app, start_ts, end_ts
                FROM app_sessions
                ORDER BY start_ts DESC
                LIMIT ?
                """,
                (limit,),
            )
            return cur.fetchall()

    def get_sessions_by_date(self, date_str):
        with self.db_lock:
            cur = self.conn.cursor()
            cur.execute(
                """
                SELECT id, app, start_ts, end_ts
                FROM app_sessions
                WHERE DATE(start_ts, 'unixepoch') = ?
                ORDER BY start_ts
                """,
                (date_str,),
            )
            return cur.fetchall()

    def get_total_duration_for_date(self, date_str):
        with self.db_lock:
            cur = self.conn.cursor()
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
            return result or 0

    def close(self):
        with self.db_lock:
            self.conn.close()


# ---- Public API (keeps callers unchanged) ----

_db = Database()


def init():
    # Singleton initializes itself
    pass


def start_session(app, start_ts):
    return _db.start_session(app, start_ts)


def end_session(session_id, end_ts):
    _db.end_session(session_id, end_ts)


def get_last_sessions(limit):
    return _db.get_last_sessions(limit)


def get_sessions_by_date(date_str):
    return _db.get_sessions_by_date(date_str)


def get_total_duration_for_date(date_str):
    return _db.get_total_duration_for_date(date_str)


def close():
    _db.close()
