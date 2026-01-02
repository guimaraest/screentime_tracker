import time
import threading
import ctypes
import os
import psutil
import signal
from collections import deque

import glfw

import db
from constants import *


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

        self.window = None
        self.worker_thread = None

        # Track whether any app was active in last N polls
        self.recent_activity = deque(maxlen=10)

    def stop(self, *_):
        self.running = False

    # ---------------- DB session logic ----------------

    def close_current_session(self):
        if self.current_session_id is not None:
            db.end_session(self.current_session_id, time.time())
            self.current_session_id = None
            self.current_app = None

    def start_new_session(self, app):
        self.current_session_id = db.start_session(app, time.time())
        self.current_app = app

    # ---------------- Worker thread ----------------

    def tracking_loop(self):
        db.init()

        try:
            while self.running:
                app = get_active_app()

                # Record recent activity
                self.recent_activity.append(app is not None)

                if app != self.current_app:
                    self.close_current_session()
                    if app:
                        self.start_new_session(app)

                time.sleep(POLL_INTERVAL)

        finally:
            self.close_current_session()
            db.close()

    # ---------------- Window ----------------

    def init_window(self):
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        self.window = glfw.create_window(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            WINDOW_TITLE,
            None,
            None,
        )

        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create window")

        glfw.make_context_current(self.window)

        # Closing the window stops the tracker
        glfw.set_window_close_callback(self.window, lambda *_: self.stop())

    def run(self):
        self.init_window()

        self.worker_thread = threading.Thread(
            target=self.tracking_loop,
            daemon=True,
        )
        self.worker_thread.start()

        try:
            while self.running and not glfw.window_should_close(self.window):
                if any(self.recent_activity):
                    status = self.current_app or "tracking"
                else:
                    status = "idle"

                glfw.set_window_title(
                    self.window,
                    f"{WINDOW_TITLE} – {status}",
                )

                glfw.poll_events()
                time.sleep(0.01)  # keeps UI responsive

        finally:
            self.running = False
            self.worker_thread.join()
            glfw.terminate()


def main():
    tracker = ScreenTimeTracker()

    signal.signal(signal.SIGINT, tracker.stop)
    signal.signal(signal.SIGTERM, tracker.stop)

    tracker.run()


if __name__ == "__main__":
    main()
