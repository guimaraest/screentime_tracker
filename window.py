# window.py
import time
import glfw
from heartbeat import is_running

from constants import *

WIDTH = 300
HEIGHT = 80
REFRESH_INTERVAL = 1.0


def main():
    if not glfw.init():
        return

    window = glfw.create_window(WIDTH, HEIGHT, "Tracker Status", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    last_check = 0

    while not glfw.window_should_close(window):
        now = time.time()
        if now - last_check > REFRESH_INTERVAL:
            running = is_running()
            last_check = now

        if running:
            glfw.set_window_title(window, "Tracker Status – RUNNING")
        else:
            glfw.set_window_title(window, "Tracker Status – NOT RUNNING")

        glfw.poll_events()
        time.sleep(0.05)

    glfw.terminate()


if __name__ == "__main__":
    main()
