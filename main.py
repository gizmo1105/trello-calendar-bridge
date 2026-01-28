from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta, timezone
from config import CALENDAR_ID, SYNC_MARKER, SYNC_WINDOW_DAYS
from clients.trello_client import fetch_cards
from clients.gcal_client import get_calendar_service, delete_synced_events, insert_event
from mappers.calendar_mapper import build_event_from_card
from services.database_service import DatabaseService
from services.logging_service import SyncLogger


def main():
    service = get_calendar_service()
    db = DatabaseService()
    cards = fetch_cards()
    logger = SyncLogger(db.client)
    logger.start_run(cards_total=len(cards))

    processed = 0
    skipped = 0
    failed = 0
    run_error = None

    now = datetime.now(timezone.utc)
    time_min = now.isoformat().replace("+00:00", "Z")
    time_max = (now + timedelta(days=SYNC_WINDOW_DAYS)).isoformat().replace("+00:00", "Z")

    try:

        delete_synced_events(service, CALENDAR_ID, time_min, time_max, SYNC_MARKER)

        for card in cards:
            if card.get("closed") or not card.get("due"):
                skipped += 1
                continue
            
            try: 
                result = build_event_from_card(card)
                if not result:
                    skipped += 1
                    continue

                body, booking, start_dt = result
                if start_dt < now:
                    continue

                body["description"] = f"{SYNC_MARKER}\n{body.get('description','')}".strip()

                db.upsert_booking(card, booking)
                insert_event(service, CALENDAR_ID, body)
                processed += 1
            
            except Exception as e:
                failed += 1
                logger.log_failure(card_id=card.get("id", "unknown"), step="process_card", err=e)
                continue
        status = "success" if failed == 0 else "partial"
        logger.finish_run(status=status, processed=processed, skipped=skipped, failed=failed)  
    
    except Exception as e:
        run_error = f"{type(e).__name__}: {str(e)}"
        logger.finish_run(status="failed", processed=processed, skipped=skipped, failed=failed, run_error=run_error)
        raise
        

if __name__ == "__main__":
    main()
