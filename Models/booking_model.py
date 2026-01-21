import unicodedata
from typing import Optional

def _normalize_label(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))

LABEL_TO_ATTR = {
    "nafn": "nafn",
    "kennitala greidanda": "kennitala_greidanda",
    "kennitala greiðanda": "kennitala_greidanda",
    "netfang": "netfang",
    "simanumer": "simanumer",
    "símanúmer": "simanumer",
    "sími": "simanumer",
    "simi": "simanumer",
    "dagsetning vidburdar": "dagsetning_vidburdar",
    "dagsetning viðburðar": "dagsetning_vidburdar",
    "timasetning vidburdar": "timasetning_vidburdar",
    "tímasetning viðburðar": "timasetning_vidburdar",
    "stadsetning": "stadsetning",
    "staðsetning": "stadsetning",
    "annad": "annad",
    "annað": "annad",
    "osk um bakgrunn": "osk_um_bakgrunn",
    "ósk um bakgrunn": "osk_um_bakgrunn",
    "pakka tilbod": "pakka_tilbod",
    "pakka tilboð": "pakka_tilbod",
    "ljosmynda prentari": "ljosmynda_prentari",
    "ljósmynda prentari": "ljosmynda_prentari",
    "skemmtilegir aukahlutir": "skemmtilegir_aukahlutir",
    "greidslumati": "greidslumati",
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
        buffer_lines = []

        def flush():
            nonlocal current_attr, buffer_lines
            if current_attr is not None:
                text = "\n".join(buffer_lines).strip()
                if text:
                    setattr(booking, current_attr, text)
            current_attr = None
            buffer_lines = []

        for raw in desc.splitlines():
            line = raw.strip()
            if not line:
                # keep blank lines only if we're collecting a multiline value
                if current_attr is not None:
                    buffer_lines.append("")
                continue

            # If this looks like "Label: value", try to interpret it
            if ":" in line:
                label, value = line.split(":", 1)
                label_norm = _normalize_label(label)
                attr = LABEL_TO_ATTR.get(label_norm)

                if attr:
                    # New known field begins -> finish previous multiline field
                    flush()

                    value = value.strip()
                    if value:
                        setattr(booking, attr, value)
                        current_attr = None
                        buffer_lines = []
                    else:
                        # Start collecting multiline value (e.g. "Annað:" with text below)
                        current_attr = attr
                        buffer_lines = []
                    continue

            # Not a recognized field line:
            # If we're collecting multiline content, append it
            if current_attr is not None:
                buffer_lines.append(raw.rstrip())

            # else: strict mode -> ignore unknown lines

        flush()
        return booking


    def to_dict(self):
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
