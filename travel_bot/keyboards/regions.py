"""
Keyboards for Uzbekistan regions and nearby place categories.
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import UZBEKISTAN_REGIONS
from translations import t


def get_regions_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """
    Returns inline keyboard of all 13 Uzbekistan regions with localized names.
    Arranged cleanly 2 per row, with a Back button at the bottom.
    """
    buttons = []
    current_row = []

    for region_id, data in UZBEKISTAN_REGIONS.items():
        name_key = f"name_{lang}" if f"name_{lang}" in data else "name_uz"
        label = data[name_key]
        current_row.append(InlineKeyboardButton(label, callback_data=f"reg_{region_id}"))

        if len(current_row) == 2:
            buttons.append(current_row)
            current_row = []

    if current_row:
        buttons.append(current_row)

    # Back to main menu
    buttons.append([InlineKeyboardButton(t("btn_back", lang), callback_data="back_to_menu")])

    return InlineKeyboardMarkup(buttons)


def get_nearby_categories_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """
    Returns inline keyboard of nearby place categories:
    - Pharmacies (🏥 Dorixonalar)
    - Cafes (🍽 Kafelar)
    - Hotels (🏨 Mehmonxonalar)
    - Fuel stations (⛽ Yoqilg‘i shoxobchalari)
    - Banks (🏦 Banklar)
    - Stores (🏪 Do‘konlar)
    - Back button
    """
    keyboard = [
        [
            InlineKeyboardButton(t("nearby_pharmacy", lang), callback_data="near_pharmacy"),
            InlineKeyboardButton(t("nearby_cafe", lang), callback_data="near_cafe"),
        ],
        [
            InlineKeyboardButton(t("nearby_hotel", lang), callback_data="near_hotel"),
            InlineKeyboardButton(t("nearby_fuel", lang), callback_data="near_fuel"),
        ],
        [
            InlineKeyboardButton(t("nearby_bank", lang), callback_data="near_bank"),
            InlineKeyboardButton(t("nearby_shop", lang), callback_data="near_shop"),
        ],
        [
            InlineKeyboardButton(t("btn_back", lang), callback_data="back_to_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_profile_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """
    Returns profile action keyboard (Edit name, change language, back).
    """
    keyboard = [
        [InlineKeyboardButton(t("btn_edit_name", lang), callback_data="prof_edit_name")],
        [InlineKeyboardButton(t("btn_change_language", lang), callback_data="prof_change_lang")],
        [InlineKeyboardButton(t("btn_back", lang), callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)
