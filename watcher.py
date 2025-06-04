import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Name of the script to watch and restart
SCRIPT_NAME = "terminal.py"

class Watcher(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.process = None
        self.restart_script()

    def restart_script(self):
        if self.process:
            print("Stopping the script...")
            self.process.terminate()
            self.process.wait()
        print("Starting the script...")
        self.process = subprocess.Popen(["python", SCRIPT_NAME])

    def on_modified(self, event):
        if event.src_path.endswith(SCRIPT_NAME):
            print(f"Change detected in {SCRIPT_NAME}. Restarting...")
            self.restart_script()

def main():
    path = "."  # Watch the current directory
    event_handler = Watcher()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Watcher stopped.")
        observer.stop()

    observer.join()
    if event_handler.process:
        event_handler.process.terminate()
        event_handler.process.wait()

if __name__ == "__main__":
    main()
