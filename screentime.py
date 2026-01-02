import numpy as np
import pygame as pg
import time
import json
import ctypes
import os
import psutil

def active_app():
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    current_pid = os.getpid()
    if pid.value == current_pid:
        return None
    process = psutil.Process(pid.value)
    return process.name()


def screentime_loop(temp_file):
    app_data = {}
    last_app = None
    app_start_time = time.time()
    save_start_time = time.time()

    while True:
        current_app = active_app()

        if current_app != last_app:

            if last_app:
                duration = time.time() - app_start_time
                app_data[last_app] = app_data.get(last_app, 0) + duration

            app_start_time = time.time()
            last_app = current_app

        if time.time() - save_start_time >= 60:
            if last_app:
                duration = time.time() - app_start_time
                app_data[last_app] = app_data.get(last_app, 0) + duration
                app_start_time = time.time()

            with open(temp_file, 'w') as f:
                json.dump(app_data, f)

            save_start_time = time.time()

        time.sleep(10)

def save_to_master(master_file, temp_file):
    if os.path.exists(temp_file):
        with open(temp_file, 'r') as f:
            try:
                temp_data = json.load(f)
            except json.JSONDecodeError:
                temp_data = {}

        if temp_data:
            new_entry = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'process_status': 'unprocessed',
                'data': temp_data
            }

            if os.path.exists(master_file):
                with open(master_file, 'r') as f:
                    try:
                        master_data = json.load(f)
                    except json.JSONDecodeError:
                        master_data = []
            else:
                master_data = []

            master_data.append(new_entry)

            with open(master_file, 'w') as f:
                json.dump(master_data, f, indent=4)

        with open(temp_file, 'w') as f:
            json.dump({}, f)

def main():
    temp_file = 'screen_time_temp.json'
    master_file = 'screen_time_master.json'
    save_to_master(master_file, temp_file)
    screentime_loop(temp_file)

if __name__ == '__main__':
    main()
