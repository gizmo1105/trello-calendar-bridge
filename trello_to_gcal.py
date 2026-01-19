import os
import json
from datetime import datetime, timedelta, timezone

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- Config from environment (set via GitHub Secrets) ---

TRELLO_KEY = os.environ["TRELLO_KEY"]
TRELLO_TOKEN = os.environ["TRELLO_TOKEN"]
BOARD_ID = os.environ["TRELLO_BOARD_ID"]

CALENDAR_ID = os.environ["GOOGLE_CALENDAR_ID"]
SERVICE_ACCOUNT_JSON = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]  # full JSON string


def get_calendar_service():
    info = json.loads(SERVICE_ACCOUNT_JSON)
    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    service = build("calendar", "v3", credentials=creds)
    return service


def fetch_trello_cards():
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/cards"
    params = {
        "key": TRELLO_KEY,
        "token": TRELLO_TOKEN,
        "fields": "id,name,desc,due,url,closed"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def trello_due_to_iso(due):
    if not due:
        return None
    # Trello due is ISO8601, often with Z
    dt = datetime.fromisoformat(due.replace("Z", "+00:00")).astimezone(timezone.utc)
    return dt.isoformat()


def build_event_from_card(card):
    start_iso = trello_due_to_iso(card["due"])
    if not start_iso:
        return None

    start_dt = datetime.fromisoformat(start_iso)
    end_dt = start_dt + timedelta(hours=1)  # default 1-hour event

    return {
        "summary": card["name"],
        "description": (card.get("desc") or "") + "\n\n" + card["url"],
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "UTC",
        },
    }


def main():
    service = get_calendar_service()
    cards = fetch_trello_cards()

    marker = "[TRELLO_SYNC]"

    now = datetime.utcnow()
    time_min = (now - timedelta(days=30)).isoformat() + "Z"
    time_max = (now + timedelta(days=365)).isoformat() + "Z"

    existing = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    existing_events = existing.get("items", [])

    # Delete previous synced events
    for event in existing_events:
        desc = event.get("description", "") or ""
        if marker in desc:
            service.events().delete(
                calendarId=CALENDAR_ID,
                eventId=event["id"]
            ).execute()

    # Create events from Trello cards
    for card in cards:
        if card.get("closed") or not card.get("due"):
            continue

        body = build_event_from_card(card)
        if not body:
            continue

        if body["description"]:
            body["description"] = f"{marker}\n" + body["description"]
        else:
            body["description"] = marker

        service.events().insert(
            calendarId=CALENDAR_ID,
            body=body
        ).execute()


if __name__ == "__main__":
    main()
