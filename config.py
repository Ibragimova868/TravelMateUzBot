"""
Configuration module for Sayohatchi Telegram Bot.
Loads environment variables, defines default settings, and constants.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file (try python-dotenv first, with standard file fallback)
ENV_FILE = BASE_DIR / ".env"
try:
    from dotenv import load_dotenv

    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE)
    else:
        load_dotenv()
except ImportError:
    # Graceful standard library .env parser
    if ENV_FILE.exists():
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# OpenRouteService API Key
OPENROUTESERVICE_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY", "").strip()

# Database File Path
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "travel_bot.db"))

# Optional Google Places API Key
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()

# Supported Languages
SUPPORTED_LANGUAGES = ["uz", "ru", "en"]
DEFAULT_LANGUAGE = "uz"

# Request Timeout (seconds)
HTTP_TIMEOUT = 12

# Uzbekistan exactly 12 Regions with predefined coordinates for Open-Meteo weather
class RegionsDict(dict):
    """
    Dictionary mapping for Uzbekistan regions supporting both Uzbek and English key lookups.
    Contains exactly the 12 administrative regions specified.
    """
    ALIASES = {
        "bukhara": "buxoro",
        "fergana": "fargona",
        "andijan": "andijon",
        "kashkadarya": "qashqadaryo",
        "khorezm": "xorazm",
        "surkhandarya": "surxondaryo",
        "tashkent": "toshkent",
        "samarkand": "samarqand",
        "jizzakh": "jizzax",
    }

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        aliased = self.ALIASES.get(key)
        if aliased and aliased in self:
            return super().__getitem__(aliased)
        raise KeyError(key)

    def get(self, key, default=None):
        if key in self:
            return super().get(key, default)
        aliased = self.ALIASES.get(key)
        if aliased and aliased in self:
            return super().get(aliased, default)
        return default


UZBEKISTAN_REGIONS = RegionsDict({
    "sirdaryo": {
        "name_uz": "Sirdaryo",
        "name_ru": "Сырдарья",
        "name_en": "Sirdaryo",
        "lat": 40.4897,
        "lon": 68.7842,
    },
    "navoiy": {
        "name_uz": "Navoiy",
        "name_ru": "Навои",
        "name_en": "Navoiy",
        "lat": 40.0844,
        "lon": 65.3792,
    },
    "jizzax": {
        "name_uz": "Jizzax",
        "name_ru": "Джизак",
        "name_en": "Jizzakh",
        "lat": 40.1158,
        "lon": 67.8422,
    },
    "xorazm": {
        "name_uz": "Xorazm",
        "name_ru": "Хорезм",
        "name_en": "Khorezm",
        "lat": 41.5500,
        "lon": 60.6333,
    },
    "buxoro": {
        "name_uz": "Buxoro",
        "name_ru": "Бухара",
        "name_en": "Bukhara",
        "lat": 39.7747,
        "lon": 64.4286,
    },
    "surxondaryo": {
        "name_uz": "Surxondaryo",
        "name_ru": "Сурхандарья",
        "name_en": "Surkhandarya",
        "lat": 37.2242,
        "lon": 67.2783,
    },
    "namangan": {
        "name_uz": "Namangan",
        "name_ru": "Наманган",
        "name_en": "Namangan",
        "lat": 40.9983,
        "lon": 71.6726,
    },
    "andijon": {
        "name_uz": "Andijon",
        "name_ru": "Андижан",
        "name_en": "Andijan",
        "lat": 40.7821,
        "lon": 72.3442,
    },
    "qashqadaryo": {
        "name_uz": "Qashqadaryo",
        "name_ru": "Кашкадарья",
        "name_en": "Kashkadarya",
        "lat": 38.8606,
        "lon": 65.7890,
    },
    "samarqand": {
        "name_uz": "Samarqand",
        "name_ru": "Самарканд",
        "name_en": "Samarkand",
        "lat": 39.6542,
        "lon": 66.9597,
    },
    "fargona": {
        "name_uz": "Farg‘ona",
        "name_ru": "Фергана",
        "name_en": "Fergana",
        "lat": 40.3842,
        "lon": 71.7843,
    },
    "toshkent": {
        "name_uz": "Toshkent",
        "name_ru": "Ташкент",
        "name_en": "Tashkent",
        "lat": 41.2995,
        "lon": 69.2401,
    },
})
