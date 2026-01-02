from pathlib import Path

# Database
DB_PATH = Path("screen_time.db")

POLL_INTERVAL = 5

# Export / CLI
DEFAULT_EXPORT_LIMIT = 100
DEFAULT_EXPORT_FILE = Path("last_sessions.csv")

# Window
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 80
WINDOW_TITLE = "Tracker Status"
WINDOW_REFRESH_INTERVAL = 1.0   # seconds
