from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta, timezone
from config import CALENDAR_ID, SYNC_MARKER, SYNC_WINDOW_DAYS
from clients.trello_client import fetch_cards
from clients.gcal_client import get_calendar_service, delete_synced_events, insert_event
from Mappers.calendar_mapper import build_event_from_card
from Services.database_service import DatabaseService


def main():
    service = get_calendar_service()
    db = DatabaseService()
    cards = fetch_cards()

    now = datetime.now(timezone.utc)
    time_min = now.isoformat().replace("+00:00", "Z")
    time_max = (now + timedelta(days=SYNC_WINDOW_DAYS)).isoformat().replace("+00:00", "Z")

    delete_synced_events(service, CALENDAR_ID, time_min, time_max, SYNC_MARKER)

    for card in cards:
        if card.get("closed") or not card.get("due"):
            continue

        result = build_event_from_card(card)
        if not result:
            continue

        body, booking, start_dt = result
        if start_dt < now:
            continue

        body["description"] = f"{SYNC_MARKER}\n{body.get('description','')}".strip()

        db.upsert_booking(card, booking)
        insert_event(service, CALENDAR_ID, body)

if __name__ == "__main__":
    main()
