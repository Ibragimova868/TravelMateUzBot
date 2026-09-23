"""
Routing and Distance calculation conversation handler for Sayohatchi Bot.
Computes road-based routes and travel times with OpenRouteService.
"""

import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from database import get_user_language
from translations import t
from services.geocoding import geocode_address, resolve_location_input, parse_coordinates
from services.routing import calculate_route
from keyboards import (
    get_main_menu_keyboard,
    get_cancel_keyboard,
    get_transport_keyboard,
)

logger = logging.getLogger(__name__)

# Conversation States
ROUTING_ASK_ORIGIN, ROUTING_ASK_DESTINATION, ROUTING_SELECT_TRANSPORT = range(3)
ROUTE_ASK_ORIGIN = ROUTING_ASK_ORIGIN
ROUTE_ASK_DESTINATION = ROUTING_ASK_DESTINATION
ROUTE_SELECT_TRANSPORT = ROUTING_SELECT_TRANSPORT


async def route_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Initiates distance and routing calculation."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    # Reset any previous routing data
    context.user_data.pop("route_origin_name", None)
    context.user_data.pop("route_origin_lat", None)
    context.user_data.pop("route_origin_lon", None)
    context.user_data.pop("route_dest_name", None)
    context.user_data.pop("route_dest_lat", None)
    context.user_data.pop("route_dest_lon", None)

    prompt = t("route_ask_origin", lang)
    if update.message:
        await update.message.reply_text(prompt, reply_markup=get_cancel_keyboard(lang))
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            prompt, reply_markup=get_cancel_keyboard(lang)
        )

    return ROUTE_ASK_ORIGIN


async def route_origin_received(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Processes origin input (address or coordinates) and asks for destination."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    text = (update.message.text or "").strip()

    # Check for cancel buttons
    if text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "🔙 Orqaga", "🔙 Назад", "🔙 Back"]:
        return await route_cancel(update, context)

    # Input length validation
    if len(text) > 100:
        await update.message.reply_text(
            t("input_too_long", lang),
            reply_markup=get_cancel_keyboard(lang),
        )
        return ROUTE_ASK_ORIGIN

    # Resolve origin location (handles both addresses and direct coordinates)
    loc = resolve_location_input(text)
    if not loc.get("success"):
        err_key = loc.get("error_key") or "route_address_not_found"
        if err_key == "invalid_coordinates":
            err_msg = t("invalid_coordinates", lang)
        elif err_key == "invalid_input":
            err_msg = t("invalid_input", lang)
        else:
            err_msg = t("route_address_not_found", lang, query=text)

        await update.message.reply_text(
            err_msg,
            reply_markup=get_cancel_keyboard(lang),
        )
        return ROUTE_ASK_ORIGIN

    context.user_data["route_origin_name"] = loc["display_name"]
    context.user_data["route_origin_lat"] = loc["lat"]
    context.user_data["route_origin_lon"] = loc["lon"]

    # Ask for destination
    await update.message.reply_text(
        t("route_ask_destination", lang),
        reply_markup=get_cancel_keyboard(lang),
    )
    return ROUTE_ASK_DESTINATION


async def route_destination_received(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Processes destination input (address or coordinates) and presents transport options."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    text = (update.message.text or "").strip()

    # Check for cancel
    if text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "🔙 Orqaga", "🔙 Назад", "🔙 Back"]:
        return await route_cancel(update, context)

    if len(text) > 100:
        await update.message.reply_text(
            t("input_too_long", lang),
            reply_markup=get_cancel_keyboard(lang),
        )
        return ROUTE_ASK_DESTINATION

    # Resolve destination location (handles both addresses and direct coordinates)
    loc = resolve_location_input(text)
    if not loc.get("success"):
        err_key = loc.get("error_key") or "route_address_not_found"
        if err_key == "invalid_coordinates":
            err_msg = t("invalid_coordinates", lang)
        elif err_key == "invalid_input":
            err_msg = t("invalid_input", lang)
        else:
            err_msg = t("route_address_not_found", lang, query=text)

        await update.message.reply_text(
            err_msg,
            reply_markup=get_cancel_keyboard(lang),
        )
        return ROUTE_ASK_DESTINATION

    context.user_data["route_dest_name"] = loc["display_name"]
    context.user_data["route_dest_lat"] = loc["lat"]
    context.user_data["route_dest_lon"] = loc["lon"]

    # Show transport options
    await update.message.reply_text(
        t("route_select_transport", lang),
        reply_markup=get_transport_keyboard(lang),
    )
    return ROUTE_SELECT_TRANSPORT


async def route_transport_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Calculates route and displays formatted distance, duration, and road details."""
    query = update.callback_query
    await query.answer()
    data = query.data

    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    if data == "tr_cancel":
        await query.edit_message_text(t("cancelled", lang))
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=t("menu_title", lang),
                reply_markup=get_main_menu_keyboard(lang),
            )
        return ConversationHandler.END

    # Extract transport key
    transport_key = data.replace("tr_", "")

    origin_name = context.user_data.get("route_origin_name", "Noma'lum manzil")
    origin_lat = context.user_data.get("route_origin_lat")
    origin_lon = context.user_data.get("route_origin_lon")

    dest_name = context.user_data.get("route_dest_name", "Noma'lum manzil")
    dest_lat = context.user_data.get("route_dest_lat")
    dest_lon = context.user_data.get("route_dest_lon")

    if not all([origin_lat, origin_lon, dest_lat, dest_lon]):
        await query.edit_message_text(t("service_error", lang))
        return ConversationHandler.END

    # Inform user that calculation is in progress
    await query.edit_message_text(t("route_calculating", lang))

    # Calculate actual road distance and time via OpenRouteService
    route_result = calculate_route(
        start_lat=origin_lat,
        start_lon=origin_lon,
        end_lat=dest_lat,
        end_lon=dest_lon,
        transport_key=transport_key,
        lang=lang,
    )

    if not route_result.get("success"):
        await query.edit_message_text(t("route_calc_error", lang))
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=t("menu_title", lang),
                reply_markup=get_main_menu_keyboard(lang),
            )
        return ConversationHandler.END

    # Map transport label
    transport_labels = {
        "foot-walking": t("transport_walk", lang),
        "cycling-regular": t("transport_bike", lang),
        "motorcycle": t("transport_moto", lang),
        "driving-car": t("transport_car", lang),
    }
    transport_display = transport_labels.get(
        transport_key, t("transport_car", lang)
    )

    # Format result string strictly as requested
    result_text = (
        f"{t('route_result_header', lang)}\n\n"
        f"{t('route_origin_label', lang, origin=origin_name)}\n\n"
        f"{t('route_destination_label', lang, destination=dest_name)}\n\n"
        f"{t('route_transport_label', lang, transport=transport_display)}\n\n"
        f"{t('route_distance_label', lang, distance=route_result['formatted_distance'])}\n\n"
        f"{t('route_duration_label', lang, duration=route_result['formatted_duration'])}"
    )

    await query.edit_message_text(result_text)

    # Send persistent main menu keyboard
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("menu_title", lang),
            reply_markup=get_main_menu_keyboard(lang),
        )

    # Clear routing data
    context.user_data.pop("route_origin_name", None)
    context.user_data.pop("route_origin_lat", None)
    context.user_data.pop("route_origin_lon", None)
    context.user_data.pop("route_dest_name", None)
    context.user_data.pop("route_dest_lat", None)
    context.user_data.pop("route_dest_lon", None)

    return ConversationHandler.END


async def route_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels ongoing route conversation."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    context.user_data.pop("route_origin_name", None)
    context.user_data.pop("route_origin_lat", None)
    context.user_data.pop("route_origin_lon", None)
    context.user_data.pop("route_dest_name", None)
    context.user_data.pop("route_dest_lat", None)
    context.user_data.pop("route_dest_lon", None)

    msg = t("cancelled", lang)
    if update.message:
        await update.message.reply_text(msg, reply_markup=get_main_menu_keyboard(lang))
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg)

    return ConversationHandler.END


def get_routing_handler() -> ConversationHandler:
    """Builds and returns the ConversationHandler for distance & routing."""
    return ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex(
                    r"^(📍 Masofa va yo‘l vaqti|📍 Расстояние и время в пути|📍 Distance & Travel Time)$"
                ),
                route_start,
            ),
            CommandHandler("route", route_start),
            CommandHandler("distance", route_start),
        ],
        states={
            ROUTE_ASK_ORIGIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, route_origin_received)
            ],
            ROUTE_ASK_DESTINATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, route_destination_received)
            ],
            ROUTE_SELECT_TRANSPORT: [
                CallbackQueryHandler(route_transport_callback, pattern="^tr_")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", route_cancel),
            MessageHandler(
                filters.Regex(r"^(❌ Bekor qilish|❌ Отмена|❌ Cancel|🔙 Orqaga|🔙 Назад|🔙 Back)$"),
                route_cancel,
            ),
        ],
        allow_reentry=True,
    )
