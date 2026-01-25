from datetime import datetime, timedelta, timezone
from config import LABEL_COLOR_TO_GCAL, DEFAULT_EVENT_DURATION_HOURS
from Models.booking_model import Booking

def build_description(card):
    booking = Booking.from_description(card.get("desc") or "")

    parts = []
    if booking.nafn: parts.append(f"Nafn: {booking.nafn}")
    if booking.kennitala_greidanda: parts.append(f"Kennitala greiðanda: {booking.kennitala_greidanda}")
    if booking.netfang: parts.append(f"Netfang: {booking.netfang}")
    if booking.simanumer: parts.append(f"Símanúmer: {booking.simanumer}")
    if booking.dagsetning_vidburdar: parts.append(f"Dagsetning viðburðar: {booking.dagsetning_vidburdar}")
    if booking.timasetning_vidburdar: parts.append(f"Tímasetning viðburðar: {booking.timasetning_vidburdar}")
    if booking.osk_um_bakgrunn: parts.append(f"Ósk um bakgrunn: {booking.osk_um_bakgrunn}")
    if booking.pakka_tilbod: parts.append(f"Pakka tilboð: {booking.pakka_tilbod}")
    if booking.ljosmynda_prentari: parts.append(f"Ljósmynda prentari: {booking.ljosmynda_prentari}")
    if booking.greidslumati: parts.append(f"Greiðslumáti: {booking.greidslumati}")
    if booking.skemmtilegir_aukahlutir: parts.append(f"Skemmtilegir aukahlutir: {booking.skemmtilegir_aukahlutir}")
    if booking.annad: parts.append(f"Annað:\n{booking.annad}")

    parts.append(f"Trello card: {card['url']}")

    return "\n\n".join(parts), booking.stadsetning, booking

def build_event_from_card(card):
    due = card.get("due")
    if not due:
        return None

    start_dt = datetime.fromisoformat(due.replace("Z", "+00:00")).astimezone(timezone.utc)
    end_dt = start_dt + timedelta(hours=DEFAULT_EVENT_DURATION_HOURS)

    description, location, booking = build_description(card)

    event = {
        "summary": booking.nafn or card["name"],
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
    }

    if location:
        event["location"] = location

    labels = card.get("labels") or []
    if labels:
        trello_color = labels[0].get("color")
        color_id = LABEL_COLOR_TO_GCAL.get(trello_color)
        if color_id:
            event["colorId"] = color_id

    return event, booking, start_dt
