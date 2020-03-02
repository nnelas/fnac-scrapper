import os
from datetime import datetime

# Project directories
WORKING_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
PROJECT_DIR = os.path.join(WORKING_DIR, "fnac-scrapper")
LOGS_DIR = os.path.join(PROJECT_DIR, "logs")

# Drivers paths
DRIVERS_DIR = os.path.join(PROJECT_DIR, "drivers")
CHROME_PATH = os.path.join(DRIVERS_DIR, "mac", "chromedriver_80")

# Drivers options
HEADLESS = True

# Timers
TIMER_PAGE = 2
TIMER_OP = 1

# Logs
now = datetime.now()
file_prefix = now.strftime("%Y%m%d-%H%M%S-")
INVENTORY_FILE = os.path.join(LOGS_DIR, "".join([file_prefix, "inventory.json"]))
MATCH_FILE = os.path.join(LOGS_DIR, "".join([file_prefix, "match.json"]))
CHANGED_FILE = os.path.join(LOGS_DIR, "".join([file_prefix, "changed.json"]))
