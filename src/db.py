import sqlite3
import time
import threading
import os
import shutil
import sys
from pathlib import Path

from .constants import *

# ---- Setup persistent DB path ----

# Base path for bundled resources (PyInstaller)
if getattr(sys, "frozen", False):
    BASE_PATH = Path(sys._MEIPASS)
else:
    BASE_PATH = Path(__file__).parent

# Persistent folder in APPDATA
APPDATA_DIR = Path(os.getenv("APPDATA")) / APP_NAME
APPDATA_DIR.mkdir(parents=True, exist_ok=True)

# Path to the persistent DB
DB_PATH = APPDATA_DIR / DB_FILENAME

# If DB doesn't exist yet, either copy bundled template or create empty
BUNDLED_DB = BASE_PATH / DB_FILENAME
if not DB_PATH.exists():
    if BUNDLED_DB.exists():
        shutil.copy(BUNDLED_DB, DB_PATH)
    else:
        DB_PATH.touch()


# ---- Database class ----
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
        self.conn.execute(f"PRAGMA journal_mode={SQLITE_JOURNAL_MODE};")
        self.conn.execute(f"PRAGMA busy_timeout = {SQLITE_BUSY_TIMEOUT_MS};")
        self.db_lock = threading.Lock()

        self._setup_schema()
        self._repair_open_sessions()

    def _setup_schema(self):
        with self.db_lock:
            cur = self.conn.cursor()

            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_APP_SESSIONS} (
                    {COLUMN_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                    {COLUMN_APP} TEXT NOT NULL,
                    {COLUMN_START_TS} REAL NOT NULL,
                    {COLUMN_END_TS} REAL
                )
            """)

            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS {INDEX_APP_SESSIONS_APP}
                ON {TABLE_APP_SESSIONS}({COLUMN_APP})
            """)

            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS {INDEX_APP_SESSIONS_START}
                ON {TABLE_APP_SESSIONS}({COLUMN_START_TS})
            """)

            self.conn.commit()

    def _repair_open_sessions(self):
        now = time.time()
        with self.db_lock:
            self.conn.execute(
                f"UPDATE {TABLE_APP_SESSIONS} SET {COLUMN_END_TS} = ? WHERE {COLUMN_END_TS} IS NULL",
                (now,),
            )
            self.conn.commit()

    def start_session(self, app, start_ts):
        with self.db_lock:
            cur = self.conn.cursor()
            cur.execute(
                f"INSERT INTO {TABLE_APP_SESSIONS} ({COLUMN_APP}, {COLUMN_START_TS}) VALUES (?, ?)",
                (app, start_ts),
            )
            self.conn.commit()
            return cur.lastrowid

    def end_session(self, session_id, end_ts):
        with self.db_lock:
            self.conn.execute(
                f"UPDATE {TABLE_APP_SESSIONS} SET {COLUMN_END_TS} = ? WHERE {COLUMN_ID} = ?",
                (end_ts, session_id),
            )
            self.conn.commit()

    def get_last_sessions(self, limit):
        with self.db_lock:
            cur = self.conn.cursor()
            cur.execute(f"""
                SELECT {COLUMN_ID}, {COLUMN_APP}, {COLUMN_START_TS}, {COLUMN_END_TS}
                FROM {TABLE_APP_SESSIONS}
                ORDER BY {COLUMN_START_TS} DESC
                LIMIT ?
            """, (limit,))
            return cur.fetchall()

    def get_sessions_by_date(self, date_str):
        with self.db_lock:
            cur = self.conn.cursor()
            cur.execute(f"""
                SELECT {COLUMN_ID}, {COLUMN_APP}, {COLUMN_START_TS}, {COLUMN_END_TS}
                FROM {TABLE_APP_SESSIONS}
                WHERE DATE({COLUMN_START_TS}, 'unixepoch') = ?
                ORDER BY {COLUMN_START_TS}
            """, (date_str,))
            return cur.fetchall()

    def get_total_duration_for_date(self, date_str):
        with self.db_lock:
            cur = self.conn.cursor()
            cur.execute(f"""
                SELECT SUM({COLUMN_END_TS} - {COLUMN_START_TS})
                FROM {TABLE_APP_SESSIONS}
                WHERE {COLUMN_END_TS} IS NOT NULL
                  AND DATE({COLUMN_START_TS}, 'unixepoch') = ?
            """, (date_str,))
            result = cur.fetchone()[0]
            return result or 0

    def close(self):
        with self.db_lock:
            self.conn.close()


# ---- Public API ----

_db = Database()

def init():
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
