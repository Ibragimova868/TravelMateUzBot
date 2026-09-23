"""
Nearby places handler for Sayohatchi Bot.
Receives user GPS location and searches nearby pharmacies, cafes, hotels, fuel stations, banks, and shops.
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
from translations import t
from services.places import places_service
from keyboards import (
    get_location_keyboard,
    get_nearby_categories_keyboard,
    get_main_menu_keyboard,
)

logger = logging.getLogger(__name__)


async def nearby_menu_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Prompts user to share their Telegram GPS location."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    prompt = t("nearby_send_location_prompt", lang)
    if update.message:
        await update.message.reply_text(
            prompt, reply_markup=get_location_keyboard(lang)
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            prompt, reply_markup=get_location_keyboard(lang)
        )


async def location_received_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Stores user coordinates and displays nearby place categories."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    location = update.message.location
    if not location:
        await update.message.reply_text(
            t("invalid_input", lang), reply_markup=get_main_menu_keyboard(lang)
        )
        return

    # Store user coordinates in session
    context.user_data["user_lat"] = location.latitude
    context.user_data["user_lon"] = location.longitude

    # First send confirmation and categories
    await update.message.reply_text(
        t("nearby_location_received", lang),
        reply_markup=get_nearby_categories_keyboard(lang),
    )


async def nearby_category_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Performs search for the selected category and returns formatted places list."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    data = query.data

    category = data.replace("near_", "")

    lat = context.user_data.get("user_lat")
    lon = context.user_data.get("user_lon")

    category_labels = {
        "pharmacy": t("nearby_pharmacy", lang),
        "cafe": t("nearby_cafe", lang),
        "hotel": t("nearby_hotel", lang),
        "fuel": t("nearby_fuel", lang),
        "bank": t("nearby_bank", lang),
        "shop": t("nearby_shop", lang),
    }
    cat_label = category_labels.get(category, category)

    if lat is None or lon is None:
        # Prompt location again if session expired
        await query.edit_message_text(
            t("nearby_send_location_prompt", lang),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(t("btn_back", lang), callback_data="back_to_menu")]]
            ),
        )
        return

    # Indicate search in progress
    await query.edit_message_text(t("nearby_searching", lang, category=cat_label))

    # Execute search via PlacesService
    result = places_service.find_nearby(lat=lat, lon=lon, category=category, lang=lang)

    if not result.get("success"):
        await query.edit_message_text(
            t("nearby_error", lang),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(t("btn_back", lang), callback_data="nearby_cats")]]
            ),
        )
        return

    places = result.get("places", [])
    if not places:
        await query.edit_message_text(
            t("nearby_not_found", lang, category=cat_label),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            t("btn_back", lang), callback_data="nearby_cats"
                        )
                    ]
                ]
            ),
        )
        return

    # Build formatted list of places strictly showing:
    # 1. Place name
    # 📍 Address
    # 📏 Distance
    lines = [t("nearby_result_header", lang, category=cat_label)]
    for p in places:
        item_text = t(
            "nearby_item_format",
            lang,
            index=p["index"],
            name=p["name"],
            address=p["address"],
            distance=p["formatted_distance"],
        )
        lines.append(item_text)

    response_text = "\n".join(lines).strip()

    # Navigation buttons: change category or return to main menu
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"🔄 {t('nearby_location_received', lang).splitlines()[-1]}",
                    callback_data="nearby_cats",
                )
            ],
            [
                InlineKeyboardButton(
                    t("btn_back", lang), callback_data="back_to_menu"
                )
            ],
        ]
    )

    await query.edit_message_text(response_text, reply_markup=keyboard)


async def nearby_show_categories(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Returns to category selection inline keyboard."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    await query.edit_message_text(
        t("nearby_location_received", lang),
        reply_markup=get_nearby_categories_keyboard(lang),
    )


def register_nearby_handlers(app) -> None:
    """Registers nearby places handlers with Telegram application."""
    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^(📍 Yaqin joylarni topish|📍 Поиск мест поблизости|📍 Find Nearby Places)$"
            ),
            nearby_menu_command,
        )
    )
    app.add_handler(CommandHandler("nearby", nearby_menu_command))
    app.add_handler(MessageHandler(filters.LOCATION, location_received_handler))
    app.add_handler(CallbackQueryHandler(nearby_category_callback, pattern="^near_"))
    app.add_handler(
        CallbackQueryHandler(nearby_show_categories, pattern="^nearby_cats$")
    )
