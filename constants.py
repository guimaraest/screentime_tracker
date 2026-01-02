from pathlib import Path

# Database
# DB / paths
APP_NAME = "TGScreenTimeTracker"
DB_FILENAME = "screen_time.db"

# SQLite PRAGMA settings
SQLITE_JOURNAL_MODE = "WAL"
SQLITE_BUSY_TIMEOUT_MS = 3000

# Table names and indexes
TABLE_APP_SESSIONS = "app_sessions"
COLUMN_ID = "id"
COLUMN_APP = "app"
COLUMN_START_TS = "start_ts"
COLUMN_END_TS = "end_ts"

INDEX_APP_SESSIONS_APP = "idx_app_sessions_app"
INDEX_APP_SESSIONS_START = "idx_app_sessions_start"


POLL_INTERVAL = 5

# Export / CLI
DEFAULT_EXPORT_LIMIT = 100
DEFAULT_EXPORT_FILE = Path("last_sessions.csv")

# Window
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 40
WINDOW_TITLE = "Tracker Status"
WINDOW_REFRESH_INTERVAL = 1.0   # seconds
