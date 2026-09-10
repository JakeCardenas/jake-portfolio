import json
import os
import re
from datetime import datetime, timezone
from functools import lru_cache

DIR = os.path.dirname(os.path.abspath(__file__))

MONTHS = {
    month: number
    for number, month in enumerate(
        "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), start=1
    )
}


@lru_cache(maxsize=None)
def load(name):
    with open(os.path.join(DIR, f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


def published(display):
    """'Sep 2026' -> datetime; the stored dates carry month precision only"""
    match = re.match(r"([A-Z][a-z]{2})\w*\s+(\d{4})", display or "")
    if not match:
        return None
    return datetime(
        int(match.group(2)), MONTHS[match.group(1)], 1, tzinfo=timezone.utc
    )
