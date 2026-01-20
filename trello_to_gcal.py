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

LABEL_COLOR_TO_GCAL = {
    "green": "2",   # Sage
    "yellow": "5",  # Banana
    "orange": "6",  # Tangerine
    "red": "11",    # Tomato/Flamingo-ish
    "purple": "3",  # Grape
    "blue": "7",    # Peacock-ish
}


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
        "fields": "id,name,desc,due,url,closed,labels"
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

def extract_location_and_notes(desc: str):
    """
    Treat the *first non-empty line* of the description as the location (address),
    and the rest as notes.
    """
    if not desc:
        return None, ""

    lines = [l for l in desc.splitlines() if l.strip()]
    if not lines:
        return None, ""

    location = lines[0].strip()
    notes = "\n".join(lines[1:]) if len(lines) > 1 else ""
    return location, notes


def build_description(card):
    desc = card.get("desc") or ""
    location, notes = extract_location_and_notes(desc)

    parts = []
    if notes:
        parts.append(notes)

    # always add Trello link for easy jump-back
    parts.append(f"Trello card: {card['url']}")

    return "\n\n".join(parts), location



def build_event_from_card(card):
    # Use due as the real start time
    due = card.get("due")
    if not due:
        return None

    start_dt = datetime.fromisoformat(due.replace("Z", "+00:00")).astimezone(timezone.utc)
   
    
    end_dt = start_dt + timedelta(hours=2)  # adjust duration if needed

    description, location = build_description(card)

    event = {
        "summary": card["name"],
        "description": description,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "UTC",
        },
    }

    # If we found an address-like first line, use it as event location
    if location:
        event["location"] = location

    # Use first label to set color if present
    labels = card.get("labels") or []
    if labels:
        trello_color = labels[0].get("color")
        color_id = LABEL_COLOR_TO_GCAL.get(trello_color)
        if color_id:
            event["colorId"] = color_id

    return event



def main():
    service = get_calendar_service()
    cards = fetch_trello_cards()

    marker = "[TRELLO_SYNC]"

    now = datetime.now(timezone.utc)
    time_min = now.isoformat().replace("+00:00", "Z")
    time_max = (now + timedelta(days=365)).isoformat().replace("+00:00", "Z")


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
        
        due_str = card["due"]
        start_dt = datetime.fromisoformat(due_str.replace("Z", "+00:00")).astimezone(timezone.utc)
         # Skip cards whose event time is already in the past
        if start_dt < now:
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
