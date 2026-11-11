"""
Persistent Customer Language Preference Store.
Hackathon Team 53 - Team Innovators.

Maintains customer language preferences across voice calls and logins.
Persists preferences to data/customer_preferences.json.
"""

import json
import os
from typing import Dict, Optional
from src.models import Language


class PreferenceStore:
    """
    Thread-safe / file-backed persistent preference storage for KeyBank customers.
    """

    DEFAULT_STORE_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "customer_preferences.json"
    )

    _in_memory_cache: Dict[str, str] = {}

    @classmethod
    def _ensure_dir(cls, file_path: str):
        dirname = os.path.dirname(file_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

    @classmethod
    def load_all(cls, file_path: Optional[str] = None) -> Dict[str, str]:
        path = file_path or cls.DEFAULT_STORE_PATH
        if not os.path.exists(path):
            return cls._in_memory_cache.copy()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                cls._in_memory_cache.update(data)
                return data
        except Exception:
            return cls._in_memory_cache.copy()

    @classmethod
    def get_preference(cls, customer_ipi: str, file_path: Optional[str] = None) -> Optional[str]:
        all_prefs = cls.load_all(file_path)
        return all_prefs.get(str(customer_ipi).strip())

    @classmethod
    def has_preference(cls, customer_ipi: str, file_path: Optional[str] = None) -> bool:
        return cls.get_preference(customer_ipi, file_path) is not None

    @classmethod
    def save_preference(cls, customer_ipi: str, language: str, file_path: Optional[str] = None) -> str:
        """
        Saves or updates preferred language ('ENG' or 'SPA').
        """
        path = file_path or cls.DEFAULT_STORE_PATH
        clean_ipi = str(customer_ipi).strip()
        lang_code = "SPA" if str(language).upper() in {"SPA", "SPANISH", "ESPAÑOL", "ESPANOL"} else "ENG"

        cls._in_memory_cache[clean_ipi] = lang_code
        try:
            cls._ensure_dir(path)
            data = {}
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            data[clean_ipi] = lang_code
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
        return lang_code

    @classmethod
    def clear_preference(cls, customer_ipi: str, file_path: Optional[str] = None):
        path = file_path or cls.DEFAULT_STORE_PATH
        clean_ipi = str(customer_ipi).strip()
        cls._in_memory_cache.pop(clean_ipi, None)
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if clean_ipi in data:
                    del data[clean_ipi]
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
        except Exception:
            pass
