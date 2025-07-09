import time
import os
import sys

LOG_PATH = os.path.join('logs', 'aioredis_queue.log')

RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

KEYWORDS = ['ERROR', 'WARNING', 'Traceback']

print(f"Monitoring {LOG_PATH} for errors and warnings...")

try:
    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        # Go to the end of the file
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            if 'ERROR' in line or 'Traceback' in line:
                print(f"{RED}{line.strip()}{RESET}")
            elif 'WARNING' in line:
                print(f"{YELLOW}{line.strip()}{RESET}")
except KeyboardInterrupt:
    print("\nLog monitor stopped.")
except FileNotFoundError:
    print(f"Log file {LOG_PATH} not found. Start the worker first.") 