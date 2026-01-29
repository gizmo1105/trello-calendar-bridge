"""
Database service for Supabase interactions.

"""


import os
from datetime import datetime, timezone
from supabase import create_client, Client



class DatabaseService:
    """
    Supabase database service for managing bookings.   
    """
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise RuntimeError("Supabase credentials missing")
        self.client: Client = create_client(url, key)

    def upsert_booking(self, card, booking, service_flags):
        """
        Upsert a booking record into the database.  

        Args:
            card: Trello card dictionary.
            booking: Booking object with details.
        Returns:
            None
        """
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
            "extras": booking.skemmtilegir_aukahlutir,
            "payment_option": booking.greidslumati,
            **service_flags,
            "updated_on": datetime.now(timezone.utc).isoformat(),

        }

        self.client.table("bookings").upsert(
            data,
            on_conflict="card_id"
        ).execute()
