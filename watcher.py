import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time
from scipy.signal import find_peaks
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from scipy.interpolate import make_interp_spline
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import sys
import os

SCRIPT_NAME = "divyansh.py"  # Change this to your main script if needed

class Watcher(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.process = None
        self.restart_script()

    def restart_script(self):
        if self.process:
            print("Stopping script...")
            self.process.terminate()
            self.process.wait()
        print("Starting the script...")
        # Use sys.executable for the current Python interpreter
        self.process = subprocess.Popen([sys.executable, SCRIPT_NAME])

    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.event_type in ("modified", "created", "deleted", "moved"):
            print(f"Detected change: {event.src_path} ({event.event_type})")
            self.restart_script()

def main():
    path = os.path.dirname(os.path.abspath(__file__))
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
            event_handler.process.wait()
    observer.join()

if __name__ == "__main__":
    main()
