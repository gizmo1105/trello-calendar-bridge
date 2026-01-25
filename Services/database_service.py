import os
from datetime import datetime, timezone

from supabase import create_client, Client



class DatabaseService:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise RuntimeError("Supabase credentials missing")
        self.client: Client = create_client(url, key)

    def upsert_booking(self, card, booking):
        data = {
            "card_id": card["id"],
            "trello_url": card["url"],
            "card_name": card["name"],
            "event_date": card["due"],

            "name": booking.nafn,
            "sid": booking.kennitala_greidanda.replace("-", "") if booking.kennitala_greidanda else None,
            "email": booking.netfang,
            "mobile": booking.simanumer,
            "event_time": booking.timasetning_vidburdar,
            "location": booking.stadsetning,
            "notes": booking.annad,
            "backdrops": booking.osk_um_bakgrunn,
            "combo": booking.pakka_tilbod,
            "printer_info": booking.ljosmynda_prentari,
            "extras": booking.skemmtilegir_aukahlutir,
            "payment_option": booking.greidslumati,
            "updated_on": datetime.now(timezone.utc).isoformat(),

        }

        self.client.table("bookings").upsert(
            data,
            on_conflict="card_id"
        ).execute()
