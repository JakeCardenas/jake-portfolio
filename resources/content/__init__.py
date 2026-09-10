import json
import os
from functools import lru_cache

DIR = os.path.dirname(os.path.abspath(__file__))


@lru_cache(maxsize=None)
def load(name):
    with open(os.path.join(DIR, f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)
