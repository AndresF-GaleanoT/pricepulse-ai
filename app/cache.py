import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

from app.config import CACHE_TTL_HOURS

CACHE_DIR = Path(os.getenv("CACHE_DIR", "cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_key(producto: str) -> str:
    return hashlib.md5(producto.lower().strip().encode()).hexdigest()


def get_cache(producto: str):
    key = _get_cache_key(producto)
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        data = json.loads(cache_file.read_text())
        cached_at = datetime.fromisoformat(data["timestamp"])
        if datetime.now() - cached_at < timedelta(hours=CACHE_TTL_HOURS):
            return data["results"]
    return None


def set_cache(producto: str, results: list):
    key = _get_cache_key(producto)
    cache_file = CACHE_DIR / f"{key}.json"
    cache_file.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "results": results
    }))
