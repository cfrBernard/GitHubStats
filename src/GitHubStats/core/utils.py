import threading
import time

def start_auto_refresh(callback, interval_sec=1800):
    def loop():
        while True:
            callback()
            time.sleep(interval_sec)
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
