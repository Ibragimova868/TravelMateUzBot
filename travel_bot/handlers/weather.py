"""
Weather forecast handler for Sayohatchi Bot.
Displays 13 Uzbekistan regions and 7-day weather forecasts via Open-Meteo.
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from database import get_user_language
from config import UZBEKISTAN_REGIONS
from translations import t
from services.weather import fetch_7day_weather
from keyboards import get_regions_keyboard

logger = logging.getLogger(__name__)


async def weather_menu_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Shows the list of 13 regions to choose from."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    text = t("weather_select_region", lang)
    if update.message:
        await update.message.reply_text(text, reply_markup=get_regions_keyboard(lang))
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, reply_markup=get_regions_keyboard(lang)
        )


async def region_selected_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Fetches and displays 7-day weather forecast for the selected region."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    data = query.data

    region_id = data.replace("reg_", "")
    region_info = UZBEKISTAN_REGIONS.get(region_id)

    if not region_info:
        await query.edit_message_text(
            t("weather_error", lang), reply_markup=get_regions_keyboard(lang)
        )
        return

    name_key = f"name_{lang}" if f"name_{lang}" in region_info else "name_uz"
    region_name = region_info[name_key]
    lat = region_info["lat"]
    lon = region_info["lon"]

    # Inform user while fetching
    await query.edit_message_text("⏳ " + t("weather_header", lang, region=region_name))

    # Fetch 7-day weather from Open-Meteo
    weather_res = fetch_7day_weather(lat, lon, region_name, lang)

    if not weather_res.get("success"):
        await query.edit_message_text(
            t("weather_error", lang),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(t("btn_back", lang), callback_data="weather_list")]]
            ),
        )
        return

    # Navigation buttons: change region or return to main menu
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"🔄 {t('weather_select_region', lang).splitlines()[0]}",
                    callback_data="weather_list",
                )
            ],
            [
                InlineKeyboardButton(
                    t("btn_back", lang), callback_data="back_to_menu"
                )
            ],
        ]
    )

    await query.edit_message_text(weather_res["formatted_text"], reply_markup=keyboard)


def register_weather_handlers(app) -> None:
    """Registers weather handlers with the Telegram application."""
    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^(🌤️ 1 haftalik ob-havo|🌤️ Погода на 7 дней|🌤️ 7-Day Weather Forecast)$"
            ),
            weather_menu_command,
        )
    )
    app.add_handler(CommandHandler("weather", weather_menu_command))
    app.add_handler(CallbackQueryHandler(region_selected_callback, pattern="^reg_"))
    app.add_handler(CallbackQueryHandler(weather_menu_command, pattern="^weather_list$"))
