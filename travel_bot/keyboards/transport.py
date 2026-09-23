"""
Transport mode selection keyboards for routing.
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from translations import t


def get_transport_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """
    Returns inline keyboard for selecting transport modes:
    - Walking (🚶 Piyoda)
    - Cycling (🚲 Velosiped)
    - Motorcycle (🏍️ Mototsikl)
    - Driving / Car (🚗 Avtomobil)
    - Cancel button (❌ Bekor qilish)
    """
    keyboard = [
        [
            InlineKeyboardButton(t("transport_walk", lang), callback_data="tr_foot-walking"),
            InlineKeyboardButton(t("transport_bike", lang), callback_data="tr_cycling-regular"),
        ],
        [
            InlineKeyboardButton(t("transport_moto", lang), callback_data="tr_motorcycle"),
            InlineKeyboardButton(t("transport_car", lang), callback_data="tr_driving-car"),
        ],
        [
            InlineKeyboardButton(t("btn_cancel", lang), callback_data="tr_cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
