import time
import ctypes
import os
import psutil
import signal

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
        self.session_start_ts = None

        self.window = None

    def stop(self, *_):
        self.running = False

    def close_current_session(self):
        if self.current_session_id is not None:
            db.end_session(self.current_session_id, time.time())

            self.current_app = None
            self.current_session_id = None
            self.session_start_ts = None

    def start_new_session(self, app):
        start_ts = time.time()
        session_id = db.start_session(app, start_ts)

        self.current_app = app
        self.current_session_id = session_id
        self.session_start_ts = start_ts

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

    def run(self):
        db.init()
        self.init_window()

        try:
            while self.running and not glfw.window_should_close(self.window):
                app = get_active_app()

                if app != self.current_app:
                    self.close_current_session()

                    if app:
                        self.start_new_session(app)

                if self.current_app:
                    glfw.set_window_title(
                        self.window,
                        f"{WINDOW_TITLE} – {self.current_app}",
                    )
                else:
                    glfw.set_window_title(
                        self.window,
                        f"{WINDOW_TITLE} – idle",
                    )

                glfw.poll_events()
                time.sleep(POLL_INTERVAL)

        finally:
            # Guaranteed cleanup
            self.close_current_session()
            db.close()
            glfw.terminate()


def main():
    tracker = ScreenTimeTracker()

    signal.signal(signal.SIGINT, tracker.stop)
    signal.signal(signal.SIGTERM, tracker.stop)

    tracker.run()


if __name__ == "__main__":
    main()
