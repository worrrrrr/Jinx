# core/preferences.py — User Preferences (persistent JSON)

import json
import os
from typing import Dict, Any, Optional

PREFERENCES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "preferences.json"
)

DEFAULT_PREFERENCES: Dict[str, Any] = {
    "language": "th",
    "emoji_level": "medium",
    "tone": "friendly",
    "max_history": 10,
    "max_tokens": 3000,
}


class UserPreferences:
    """โหลด/บันทึก Preferences จาก data/preferences.json"""

    def __init__(self, path: str = PREFERENCES_PATH):
        self.path = path
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._data = {}
        # เติมค่าที่หายไปด้วย default
        for k, v in DEFAULT_PREFERENCES.items():
            self._data.setdefault(k, v)
        self._save()

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value
        self._save()

    def set_multi(self, updates: Dict[str, Any]):
        self._data.update(updates)
        self._save()

    def reset(self):
        self._data = dict(DEFAULT_PREFERENCES)
        self._save()

    @property
    def all(self) -> Dict[str, Any]:
        return dict(self._data)
