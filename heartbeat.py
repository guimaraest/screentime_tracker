import time

from constants import *


def write_heartbeat():
    HEARTBEAT_FILE.write_text(str(time.time()))


def is_running():
    if not HEARTBEAT_FILE.exists():
        return False

    try:
        last = float(HEARTBEAT_FILE.read_text())
    except ValueError:
        return False

    return (time.time() - last) < HEARTBEAT_TIMEOUT
