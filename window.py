import time
import glfw

from heartbeat import is_running
from constants import *


def main():
    if not glfw.init():
        return

    window = glfw.create_window(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        WINDOW_TITLE,
        None,
        None,
    )
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    last_check = 0.0
    running = False

    while not glfw.window_should_close(window):
        now = time.time()

        if now - last_check >= WINDOW_REFRESH_INTERVAL:
            running = is_running()
            last_check = now

        title = (
            f"{WINDOW_TITLE} – RUNNING"
            if running
            else f"{WINDOW_TITLE} – NOT RUNNING"
        )
        glfw.set_window_title(window, title)

        glfw.poll_events()
        time.sleep(0.05)

    glfw.terminate()


if __name__ == "__main__":
    main()
