"""
Language selection keyboards for Sayohatchi Bot.
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from translations import t


def get_language_keyboard(is_change: bool = False, lang: str = "uz") -> InlineKeyboardMarkup:
    """
    Returns inline keyboard for selecting bot language.
    If is_change is True, includes a back button.
    """
    buttons = [
        [
            InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="set_lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
            InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
        ]
    ]
    if is_change:
        buttons.append([InlineKeyboardButton(t("btn_back", lang), callback_data="back_to_menu")])

    return InlineKeyboardMarkup(buttons)
