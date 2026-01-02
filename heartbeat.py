import time
from pathlib import Path

from constants import *

HEARTBEAT_FILE = Path("tracker_heartbeat.txt")
HEARTBEAT_INTERVAL = 2  # seconds


def write_heartbeat():
    HEARTBEAT_FILE.write_text(str(time.time()))


def is_running(timeout=5):
    if not HEARTBEAT_FILE.exists():
        return False

    try:
        last = float(HEARTBEAT_FILE.read_text())
    except ValueError:
        return False

    return (time.time() - last) < timeout
