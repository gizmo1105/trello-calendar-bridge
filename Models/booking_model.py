
import re
from typing import Optional

def _normalize_label(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("\u00A0", " ")  # NBSP -> space
    s = re.sub(r"\s+", " ", s)    # collapse whitespace
    return s

LABEL_TO_ATTR = {
    "nafn": "nafn",
    "kennitala greiðanda": "kennitala_greidanda",
    "netfang": "netfang",
    "símanúmer": "simanumer",
    "dagsetning viðburðar": "dagsetning_vidburdar",
    "tímasetning viðburðar": "timasetning_vidburdar",
    "staðsetning": "stadsetning",
    "annað": "annad",
    "ósk um bakgrunn": "osk_um_bakgrunn",
    "pakka tilboð": "pakka_tilbod",
    "ljósmynda prentari": "ljosmynda_prentari",
    "skemmtilegir aukahlutir": "skemmtilegir_aukahlutir",
    "greiðslumáti": "greidslumati",                    
}


class Booking:
    def __init__(
        self,
        nafn: Optional[str] = None,
        kennitala_greidanda: Optional[str] = None,
        netfang: Optional[str] = None,
        simanumer: Optional[str] = None,
        dagsetning_vidburdar: Optional[str] = None,
        timasetning_vidburdar: Optional[str] = None,
        stadsetning: Optional[str] = None,
        annad: Optional[str] = None,
        osk_um_bakgrunn: Optional[str] = None,
        pakka_tilbod: Optional[str] = None,
        ljosmynda_prentari: Optional[str] = None,
        skemmtilegir_aukahlutir: Optional[str] = None,
        greidslumati: Optional[str] = None,
    ):
        self.nafn = nafn
        self.kennitala_greidanda = kennitala_greidanda
        self.netfang = netfang
        self.simanumer = simanumer
        self.dagsetning_vidburdar = dagsetning_vidburdar
        self.timasetning_vidburdar = timasetning_vidburdar
        self.stadsetning = stadsetning
        self.annad = annad
        self.osk_um_bakgrunn = osk_um_bakgrunn
        self.pakka_tilbod = pakka_tilbod
        self.ljosmynda_prentari = ljosmynda_prentari
        self.skemmtilegir_aukahlutir = skemmtilegir_aukahlutir
        self.greidslumati = greidslumati

    @classmethod
    def from_description(cls, desc: str):
        booking = cls()
        if not desc:
            return booking

        current_attr = None
        buffer = []

        def flush():
            nonlocal current_attr, buffer
            if current_attr and buffer:
                setattr(booking, current_attr, "\n".join(buffer).strip())
            current_attr = None
            buffer = []

        for raw in desc.splitlines():
            line = raw.rstrip()
            if not line.strip():
                if current_attr:
                    buffer.append("")
                continue

            if ":" in line:
                label, value = line.split(":", 1)
                label_norm = _normalize_label(label)
                attr = LABEL_TO_ATTR.get(label_norm)
                if attr:
                    flush()
                    value = value.strip()
                    if value:
                        setattr(booking, attr, value)
                    else:
                        current_attr = attr
                        buffer = []
                    continue

            # Not a recognized label → continuation of previous field
            if current_attr:
                buffer.append(line)

        flush()
        return booking



    def to_dict(self):
        """
        Serialize the booking to a dictionary.

        Args:            
            None
        Returns:
            dict: Dictionary representation of the booking.
        """
        return {
            "nafn": self.nafn,
            "kennitala_greidanda": self.kennitala_greidanda,
            "netfang": self.netfang,
            "simanumer": self.simanumer,
            "dagsetning_vidburdar": self.dagsetning_vidburdar,
            "timasetning_vidburdar": self.timasetning_vidburdar,
            "stadsetning": self.stadsetning,
            "annad": self.annad,
            "osk_um_bakgrunn": self.osk_um_bakgrunn,
            "pakka_tilbod": self.pakka_tilbod,
            "ljosmynda_prentari": self.ljosmynda_prentari,
            "skemmtilegir_aukahlutir": self.skemmtilegir_aukahlutir,
            "greidslumati": self.greidslumati,
        }
    

    