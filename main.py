import time
import ctypes
import os
import psutil
import signal
import subprocess
import sys

from heartbeat import write_heartbeat
import db
from constants import *


def start_window():
    subprocess.Popen(
        [sys.executable, "window.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def get_active_app():
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None

        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        if pid.value == os.getpid():
            return None

        proc = psutil.Process(pid.value)
        return proc.name().lower()

    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
        return None


class ScreenTimeTracker:
    def __init__(self):
        self.running = True

        self.current_app = None
        self.current_session_id = None
        self.session_start_ts = None

    def stop(self, *_):
        self.running = False

    def close_current_session(self):
        if self.current_session_id is not None:
            end_ts = time.time()
            db.end_session(self.current_session_id, end_ts)

            self.current_app = None
            self.current_session_id = None
            self.session_start_ts = None

    def start_new_session(self, app):
        start_ts = time.time()
        session_id = db.start_session(app, start_ts)

        self.current_app = app
        self.current_session_id = session_id
        self.session_start_ts = start_ts

    def run(self):
        db.init()
        start_window()

        while self.running:
            app = get_active_app()

            if app != self.current_app:
                self.close_current_session()

                if app:
                    self.start_new_session(app)

            write_heartbeat()
            time.sleep(HEARTBEAT_INTERVAL)

        self.close_current_session()
        db.close()


def main():
    tracker = ScreenTimeTracker()

    signal.signal(signal.SIGINT, tracker.stop)
    signal.signal(signal.SIGTERM, tracker.stop)

    tracker.run()


if __name__ == "__main__":
    main()
