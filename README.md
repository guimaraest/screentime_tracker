# Screen Time Tracker

A lightweight screen time tracker for Windows that records active application usage into a local SQLite database.  
It runs as a background process, writes periodic heartbeats, and exposes a small CLI for exporting session data.

## Features

- Tracks foreground application usage
- Persists sessions in SQLite
- Crash-safe session repair on startup
- Heartbeat-based “running” detection
- Minimal GLFW status window
- CLI export to CSV
- Concurrent-safe SQLite access (WAL mode + singleton connection)

## Project Structure

```
.
├── main.py          # Tracker process
├── window.py        # Status window (RUNNING / NOT RUNNING)
├── cli.py           # CSV export CLI
├── db.py            # Database layer (singleton)
├── heartbeat.py     # Heartbeat read/write
├── constants.py     # Centralized constants
├── screen_time.db   # SQLite DB (ignored by git)
├── tracker_heartbeat.txt  # Runtime heartbeat (ignored)
└── README.md
```

## How It Works

- `main.py` polls the active foreground window at a fixed interval.
- When the active app changes, the previous session is closed and a new one is started.
- Sessions are written to SQLite using a singleton database connection.
- A heartbeat file is updated periodically to indicate liveness.
- `window.py` runs as a separate process and reads the heartbeat to display status.
- `cli.py` reads from the database and exports recent sessions to CSV.

## Requirements

- Python 3.12+
- Windows (uses `ctypes.windll.user32`)

Dependencies:

- psutil
- glfw

Install dependencies:

```bash
pip install psutil glfw
```

## Running the Tracker

Start the tracker:

```bash
python main.py
```

This will:

- Initialize the database if needed
- Start tracking active applications
- Launch the status window automatically

Stop the tracker with:

```text
Ctrl + C
```

## Status Window

The GLFW window displays:

- **RUNNING** — heartbeat is fresh
- **NOT RUNNING** — tracker stopped or crashed

The window is started automatically by `main.py`.

## Exporting Data

Export recent sessions to CSV:

```bash
python cli.py
```

Optional arguments:

```bash
python cli.py --limit 200 --out sessions.csv
```

CSV columns:

```
id, app, start_ts, end_ts, duration
```

## Database Model

Table: `app_sessions`

| Column     | Type |
|-----------|------|
| id        | INT  |
| app       | TEXT |
| start_ts | REAL |
| end_ts   | REAL |

- Timestamps are Unix epoch seconds.
- Sessions left open due to crashes are auto-closed on startup.

## Concurrency Notes

- SQLite runs in WAL mode.
- A singleton DB connection is shared per process.
- Reads (CLI) and writes (tracker) can safely occur at the same time.

## Limitations

- Windows-only
- Tracks application process name, not window title
- No idle detection (keyboard/mouse)
- No UI controls (window is informational only)

## License

MIT
