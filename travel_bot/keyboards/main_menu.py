"""
Main menu keyboards for Sayohatchi Bot.
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton
from translations import t


def get_main_menu_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Returns the persistent main menu reply keyboard."""
    keyboard = [
        [
            KeyboardButton(t("btn_distance_route", lang)),
            KeyboardButton(t("btn_weather", lang)),
        ],
        [
            KeyboardButton(t("btn_nearby", lang)),
            KeyboardButton(t("btn_profile", lang)),
        ],
        [
            KeyboardButton(t("btn_change_language", lang)),
            KeyboardButton(t("btn_about", lang)),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def get_cancel_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Returns a simple cancel keyboard for ongoing conversations."""
    keyboard = [
        [KeyboardButton(t("btn_cancel", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def get_back_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Returns a back button keyboard."""
    keyboard = [
        [KeyboardButton(t("btn_back", lang))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def get_location_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Returns a keyboard with a request_location button and cancel button."""
    keyboard = [
        [KeyboardButton(t("btn_send_location", lang), request_location=True)],
        [KeyboardButton(t("btn_cancel", lang))],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
