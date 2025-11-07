import json
import os
from typing import List, Dict

WATCHLIST_PATH = "src/data/watchlist.json"


def _ensure_dir():
    os.makedirs(os.path.dirname(WATCHLIST_PATH), exist_ok=True)


def load_watchlist() -> List[Dict[str, str]]:
    _ensure_dir()
    if not os.path.exists(WATCHLIST_PATH):
        return []
    try:
        with open(WATCHLIST_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return []


def save_watchlist(items: List[Dict[str, str]]):
    _ensure_dir()
    with open(WATCHLIST_PATH, "w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=2)


def add_watchlist(url: str, note: str | None = None) -> None:
    items = load_watchlist()
    items.append({"url": url, "note": note or ""})
    save_watchlist(items)


def view_watchlist() -> List[Dict[str, str]]:
    return load_watchlist()


def remove_watchlist(index: int) -> bool:
    items = load_watchlist()
    if index < 0 or index >= len(items):
        return False
    items.pop(index)
    save_watchlist(items)
    return True
