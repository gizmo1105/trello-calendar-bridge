import os
import json

# --- Config from environment (set via GitHub Secrets) ---

TRELLO_KEY = os.environ["TRELLO_KEY"]
TRELLO_TOKEN = os.environ["TRELLO_TOKEN"]
BOARD_ID = os.environ["TRELLO_BOARD_ID"]

CALENDAR_ID = os.environ["GOOGLE_CALENDAR_ID"]
SERVICE_ACCOUNT_JSON = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]  # full JSON string


LABEL_COLOR_TO_GCAL = {
    "green": "2",   # Sage
    "yellow": "5",  # Banana
    "orange": "6",  # Tangerine
    "red": "11",    # Tomato/Flamingo-ish
    "purple": "3",  # Grape
    "blue": "7",    # Peacock-ish
}

SYNC_MARKER = "[TRELLO_SYNC]"
SYNC_WINDOW_DAYS = 365
DEFAULT_EVENT_DURATION_HOURS = 1

def service_account_info():
    return json.loads(SERVICE_ACCOUNT_JSON)