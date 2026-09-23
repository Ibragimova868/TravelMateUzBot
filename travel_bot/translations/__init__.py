"""
Translation manager module for Sayohatchi Bot.
Provides localized string lookup with fallback and parameter interpolation.
"""

from typing import Any, Dict
from translations.uz import MESSAGES as UZ_MESSAGES
from translations.ru import MESSAGES as RU_MESSAGES
from translations.en import MESSAGES as EN_MESSAGES

LANGUAGES: Dict[str, Dict[str, Any]] = {
    "uz": UZ_MESSAGES,
    "ru": RU_MESSAGES,
    "en": EN_MESSAGES,
}

LANGUAGE_NAMES = {
    "uz": "O‘zbek",
    "ru": "Русский",
    "en": "English",
}


def t(key: str, lang: str = "uz", **kwargs: Any) -> str:
    """
    Retrieves the translated text for `key` in `lang`.
    Falls back to 'uz' then 'en' if key is missing.
    Interpolates any provided kwargs safely.
    """
    lang_dict = LANGUAGES.get(lang, UZ_MESSAGES)
    text = lang_dict.get(key)

    if text is None:
        # Fallback to uz
        text = UZ_MESSAGES.get(key)
    if text is None:
        # Fallback to en
        text = EN_MESSAGES.get(key, key)

    if not isinstance(text, str):
        return str(text)

    try:
        return text.format(**kwargs)
    except KeyError:
        return text
    except Exception:
        return text


def get_weekday_name(day_index: int, lang: str = "uz") -> str:
    """Returns localized weekday name (0=Monday, 6=Sunday)."""
    lang_dict = LANGUAGES.get(lang, UZ_MESSAGES)
    weekdays = lang_dict.get("weekdays", {})
    return weekdays.get(day_index, f"Day {day_index}")


def get_weather_desc(weather_key: str, lang: str = "uz") -> str:
    """Returns localized weather condition description."""
    lang_dict = LANGUAGES.get(lang, UZ_MESSAGES)
    descs = lang_dict.get("weather_desc", {})
    return descs.get(weather_key, weather_key)


def get_language_display_name(lang_code: str) -> str:
    """Returns user-facing label for a language code."""
    return LANGUAGE_NAMES.get(lang_code, "🇺🇿 O‘zbek")
