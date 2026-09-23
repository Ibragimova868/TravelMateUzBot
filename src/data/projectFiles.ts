export interface FileEntry {
  path: string;
  category: 'core' | 'handler' | 'service' | 'keyboard' | 'translation' | 'config';
  language: string;
  description: string;
  content: string;
}

export const PROJECT_FILES: FileEntry[] = [
  {
    path: "services/geocoding.py",
    category: "service",
    language: "python",
    description: "Geocoding and Coordinate Parsing service. Detects/validates coordinates (lat, lon) and geocodes text addresses.",
    content: `"""
Geocoding and Coordinate Parsing service for Sayohatchi Bot.
Converts place names and addresses into geographical coordinates (lat, lon)
and detects/validates raw geographic coordinate inputs (e.g. '39.7747, 64.4286').
"""

import logging
from typing import Dict, Any, Optional, Tuple
from config import OPENROUTESERVICE_API_KEY, HTTP_TIMEOUT
from services.http_client import http_get

logger = logging.getLogger(__name__)


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validates that latitude is in [-90, 90] and longitude is in [-180, 180]."""
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def parse_coordinates(text: str) -> Optional[Tuple[float, float]]:
    """
    Parses a string containing latitude and longitude separated by a comma.
    Whitespace around values is ignored.
    Returns (lat, lon) tuple if valid, or None if the text is not valid coordinates.
    """
    clean = (text or "").strip()
    if not clean or "," not in clean:
        return None

    parts = clean.split(",")
    if len(parts) != 2:
        return None

    try:
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
    except (ValueError, TypeError):
        return None

    if not validate_coordinates(lat, lon):
        return None

    return (lat, lon)


def resolve_location_input(text: str) -> Dict[str, Any]:
    """
    Resolves user input as either:
    1. Direct valid coordinates (e.g. '39.7747, 64.4286') -> No geocoding API is invoked.
    2. Malformed or out-of-range coordinate attempt -> error_key='invalid_coordinates'.
    3. Text address (e.g. 'Bukhara', 'Tashkent') -> Geocodes address via ORS or Nominatim.
    """
    clean = (text or "").strip()
    if not clean:
        return {
            "success": False,
            "lat": None,
            "lon": None,
            "display_name": "",
            "is_coordinate": False,
            "error_key": "invalid_input",
            "error": "Empty input",
        }

    # 1. Direct valid coordinate check
    coords = parse_coordinates(clean)
    if coords is not None:
        lat, lon = coords
        return {
            "success": True,
            "lat": lat,
            "lon": lon,
            "display_name": f"{lat:.4f}, {lon:.4f}",
            "is_coordinate": True,
            "error_key": None,
            "error": None,
        }

    # 2. Check for invalid coordinate attempts
    try:
        float(clean)
        return {
            "success": False,
            "lat": None,
            "lon": None,
            "display_name": "",
            "is_coordinate": True,
            "error_key": "invalid_coordinates",
            "error": "Single coordinate provided without pair",
        }
    except ValueError:
        pass

    if "," in clean:
        parts = clean.split(",")
        if len(parts) == 2:
            p0 = parts[0].strip()
            p1 = parts[1].strip()
            try:
                lat_val = float(p0)
                lon_val = float(p1)
                if not validate_coordinates(lat_val, lon_val):
                    return {
                        "success": False,
                        "lat": None,
                        "lon": None,
                        "display_name": "",
                        "is_coordinate": True,
                        "error_key": "invalid_coordinates",
                        "error": "Coordinates out of valid range (-90..90, -180..180)",
                    }
            except ValueError:
                pass

    # 3. Text address geocoding via existing geocoding service
    geo = geocode_address(clean)
    if geo.get("success"):
        return {
            "success": True,
            "lat": geo["lat"],
            "lon": geo["lon"],
            "display_name": geo["display_name"],
            "is_coordinate": False,
            "error_key": None,
            "error": None,
        }
    else:
        return {
            "success": False,
            "lat": None,
            "lon": None,
            "display_name": "",
            "is_coordinate": False,
            "error_key": "route_address_not_found",
            "error": geo.get("error", "Address not found"),
        }


def geocode_address(query: str) -> Dict[str, Any]:
    clean_query = query.strip()
    if not clean_query:
        return {"success": False, "lat": None, "lon": None, "display_name": "", "error": "Empty query"}

    if OPENROUTESERVICE_API_KEY:
        try:
            url = "https://api.openrouteservice.org/geocode/search"
            params = {"api_key": OPENROUTESERVICE_API_KEY, "text": clean_query, "size": 1}
            response = http_get(url, params=params, timeout=HTTP_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                if features:
                    feat = features[0]
                    coords = feat.get("geometry", {}).get("coordinates", [])
                    props = feat.get("properties", {})
                    if len(coords) >= 2:
                        return {
                            "success": True,
                            "lat": float(coords[1]),
                            "lon": float(coords[0]),
                            "display_name": props.get("label", clean_query),
                            "error": None,
                        }
        except Exception as e:
            logger.warning("ORS Geocoding request error: %s. Trying fallback...", e)

    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": clean_query, "format": "json", "limit": 1, "addressdetails": 1}
        headers = {"User-Agent": "SayohatchiTelegramBot/2.0 (Uzbekistan Travel Assistant)"}
        response = http_get(url, params=params, headers=headers, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
            results = response.json()
            if results and len(results) > 0:
                first = results[0]
                display_name = first.get("display_name", clean_query)
                parts = [p.strip() for p in display_name.split(",") if p.strip()]
                short_name = ", ".join(parts[:3]) if len(parts) > 3 else display_name
                return {
                    "success": True,
                    "lat": float(first["lat"]),
                    "lon": float(first["lon"]),
                    "display_name": short_name,
                    "error": None,
                }
    except Exception as e:
        logger.error("Nominatim fallback request error: %s", e)

    return {"success": False, "lat": None, "lon": None, "display_name": "", "error": "Address not found"}
`
  },
  {
    path: "handlers/routing.py",
    category: "handler",
    language: "python",
    description: "ConversationHandler for Distance & Routing: supports both text addresses and raw coordinates (39.7747, 64.4286).",
    content: `"""
Routing and Distance calculation conversation handler for Sayohatchi Bot.
Computes road-based routes and travel times with OpenRouteService.
Supports input as either normal text addresses or geographic coordinates.
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

ROUTE_ASK_ORIGIN, ROUTE_ASK_DESTINATION, ROUTE_SELECT_TRANSPORT = range(3)


async def route_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    for k in ["route_origin_name", "route_origin_lat", "route_origin_lon", "route_dest_name", "route_dest_lat", "route_dest_lon"]:
        context.user_data.pop(k, None)

    prompt = t("route_ask_origin", lang)
    if update.message:
        await update.message.reply_text(prompt, reply_markup=get_cancel_keyboard(lang))
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(prompt, reply_markup=get_cancel_keyboard(lang))

    return ROUTE_ASK_ORIGIN


async def route_origin_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    text = (update.message.text or "").strip()

    if text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "🔙 Orqaga", "🔙 Назад", "🔙 Back"]:
        return await route_cancel(update, context)

    if len(text) > 100:
        await update.message.reply_text(t("input_too_long", lang), reply_markup=get_cancel_keyboard(lang))
        return ROUTE_ASK_ORIGIN

    loc = resolve_location_input(text)
    if not loc.get("success"):
        err_key = loc.get("error_key") or "route_address_not_found"
        if err_key == "invalid_coordinates":
            err_msg = t("invalid_coordinates", lang)
        elif err_key == "invalid_input":
            err_msg = t("invalid_input", lang)
        else:
            err_msg = t("route_address_not_found", lang, query=text)

        await update.message.reply_text(err_msg, reply_markup=get_cancel_keyboard(lang))
        return ROUTE_ASK_ORIGIN

    context.user_data["route_origin_name"] = loc["display_name"]
    context.user_data["route_origin_lat"] = loc["lat"]
    context.user_data["route_origin_lon"] = loc["lon"]

    await update.message.reply_text(t("route_ask_destination", lang), reply_markup=get_cancel_keyboard(lang))
    return ROUTE_ASK_DESTINATION


async def route_destination_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    text = (update.message.text or "").strip()

    if text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "🔙 Orqaga", "🔙 Назад", "🔙 Back"]:
        return await route_cancel(update, context)

    if len(text) > 100:
        await update.message.reply_text(t("input_too_long", lang), reply_markup=get_cancel_keyboard(lang))
        return ROUTE_ASK_DESTINATION

    loc = resolve_location_input(text)
    if not loc.get("success"):
        err_key = loc.get("error_key") or "route_address_not_found"
        if err_key == "invalid_coordinates":
            err_msg = t("invalid_coordinates", lang)
        elif err_key == "invalid_input":
            err_msg = t("invalid_input", lang)
        else:
            err_msg = t("route_address_not_found", lang, query=text)

        await update.message.reply_text(err_msg, reply_markup=get_cancel_keyboard(lang))
        return ROUTE_ASK_DESTINATION

    context.user_data["route_dest_name"] = loc["display_name"]
    context.user_data["route_dest_lat"] = loc["lat"]
    context.user_data["route_dest_lon"] = loc["lon"]

    await update.message.reply_text(t("route_select_transport", lang), reply_markup=get_transport_keyboard(lang))
    return ROUTE_SELECT_TRANSPORT


async def route_transport_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

    transport_key = data.replace("tr_", "")
    origin_name = context.user_data.get("route_origin_name", "Noma'lum manzil")
    origin_lat = context.user_data.get("route_origin_lat")
    origin_lon = context.user_data.get("route_origin_lon")

    dest_name = context.user_data.get("route_dest_name", "Noma'lum manzil")
    dest_lat = context.user_data.get("route_dest_lat")
    dest_lon = context.user_data.get("route_dest_lon")

    await query.edit_message_text(t("route_calculating", lang))

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
        return ConversationHandler.END

    transport_labels = {
        "foot-walking": t("transport_walk", lang),
        "cycling-regular": t("transport_bike", lang),
        "motorcycle": t("transport_moto", lang),
        "driving-car": t("transport_car", lang),
    }
    transport_display = transport_labels.get(transport_key, t("transport_car", lang))

    result_text = (
        f"{t('route_result_header', lang)}\\n\\n"
        f"{t('route_origin_label', lang, origin=origin_name)}\\n\\n"
        f"{t('route_destination_label', lang, destination=dest_name)}\\n\\n"
        f"{t('route_transport_label', lang, transport=transport_display)}\\n\\n"
        f"{t('route_distance_label', lang, distance=route_result['formatted_distance'])}\\n\\n"
        f"{t('route_duration_label', lang, duration=route_result['formatted_duration'])}"
    )

    await query.edit_message_text(result_text)

    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("menu_title", lang),
            reply_markup=get_main_menu_keyboard(lang),
        )

    return ConversationHandler.END


async def route_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    msg = t("cancelled", lang)
    if update.message:
        await update.message.reply_text(msg, reply_markup=get_main_menu_keyboard(lang))
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg)
    return ConversationHandler.END


def get_routing_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex(r"^(📍 Masofa va yo‘l vaqti|📍 Расстояние и время в пути|📍 Distance & Travel Time)$"),
                route_start,
            ),
            CommandHandler("route", route_start),
            CommandHandler("distance", route_start),
        ],
        states={
            ROUTE_ASK_ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, route_origin_received)],
            ROUTE_ASK_DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, route_destination_received)],
            ROUTE_SELECT_TRANSPORT: [CallbackQueryHandler(route_transport_callback, pattern="^tr_")],
        },
        fallbacks=[
            CommandHandler("cancel", route_cancel),
            MessageHandler(filters.Regex(r"^(❌ Bekor qilish|❌ Отмена|❌ Cancel|🔙 Orqaga|🔙 Назад|🔙 Back)$"), route_cancel),
        ],
        allow_reentry=True,
    )
`
  },
  {
    path: "translations/uz.py",
    category: "translation",
    language: "python",
    description: "Uzbek dictionary including invalid_coordinates and updated coordinate routing prompts.",
    content: `"""
Uzbek language dictionary for Sayohatchi Bot.
"""

MESSAGES = {
    "welcome_new_user": "Assalomu alaykum. Xush kelibsiz!",
    "btn_back": "🔙 Orqaga",
    "btn_cancel": "❌ Bekor qilish",
    "cancelled": "Jarayon bekor qilindi. Bosh menyudasiz.",
    "unknown_command": "Noma'lum buyruq yoki xabar. Iltimos, menyudagi tugmalardan foydalaning.",
    "service_error": "Xizmat vaqtincha ishlamayapti. Keyinroq qayta urinib ko‘ring.",
    "input_too_long": "Kiritilgan matn juda uzun. Iltimos, qisqaroq qilib qayta yozing (maksimal 100 ta belgi).",
    "invalid_input": "Noto‘g‘ri ma'lumot kiritildi. Iltimos, qaytadan urinib ko‘ring.",
    "invalid_coordinates": "Noto‘g‘ri koordinata kiritildi. Iltimos, quyidagi formatda kiriting:\\n39.7747, 64.4286\\n(Kenglik: -90 dan 90 gacha, Uzunlik: -180 dan 180 gacha)",
    "route_ask_origin": "Qayerdan ketasiz?\\n(Shahar/manzil nomini yoki koordinatalarni kiriting, masalan: Toshkent yoki 39.7747, 64.4286)",
    "route_ask_destination": "Qayerga borasiz?\\n(Boriladigan shahar/manzil nomini yoki koordinatalarni kiriting, masalan: Samarqand yoki 41.2995, 69.2401)",
    "route_select_transport": "Transport turini tanlang:",
    "transport_walk": "🚶 Piyoda",
    "transport_bike": "🚲 Velosiped",
    "transport_moto": "🏍️ Mototsikl",
    "transport_car": "🚗 Avtomobil",
    "route_calculating": "Yo‘nalish va masofa hisoblanmoqda, iltimos kuting...",
    "route_result_header": "🚗 Marshrut hisob-kitobi natijasi:",
    "route_origin_label": "📍 Boshlang‘ich manzil:\\n{origin}",
    "route_destination_label": "🏁 Boriladigan manzil:\\n{destination}",
    "route_transport_label": "🚗 Transport:\\n{transport}",
    "route_distance_label": "📏 Masofa:\\n{distance}",
    "route_duration_label": "⏱ Yo‘l vaqti:\\n{duration}",
    "route_address_not_found": "Kechirasiz, '{query}' manzili topilmadi. Iltimos, manzil nomini to‘g‘riroq yoki kengroq qilib yozing.",
    "route_calc_error": "Yo‘nalishni hisoblab bo‘lmadi. Ushbu ikki nuqta o‘rtasida to‘g‘ridan-to‘g‘ri yo‘l topilmadi yoki xizmatda xatolik yuz berdi.",
    "route_api_missing": "Yo‘nalish xizmati API kaliti sozlanmagan. Iltimos, bot ma'muriga murojaat qiling.",
}
`
  },
  {
    path: "bot.py",
    category: "core",
    language: "python",
    description: "Main application entry point. Initializes SQLite DB, registers handlers, starts polling.",
    content: `#!/usr/bin/env python3
"""
Sayohatchi Telegram Bot - Main Application Entrypoint
A complete travel, navigation, 7-day weather, and nearby-places assistant for Uzbekistan.

Supports:
- 🇺🇿 O‘zbek (default)
- 🇷🇺 Русский
- 🇬🇧 English
"""

import sys
import logging
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database import init_db
from handlers import (
    get_registration_handler,
    get_routing_handler,
    register_weather_handlers,
    register_nearby_handlers,
    get_profile_handler,
    register_language_handlers,
    register_menu_handlers,
    global_error_handler,
    unknown_message_handler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("SayohatchiBot")


def main() -> None:
    logger.info("Initializing database...")
    init_db()

    if not BOT_TOKEN:
        logger.error(
            "ERROR: BOT_TOKEN is not set!\\n"
            "Please create a .env file based on .env.example and provide your Telegram Bot Token from @BotFather."
        )
        sys.exit(1)

    logger.info("Building Telegram Application...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(get_registration_handler())
    app.add_handler(get_routing_handler())
    app.add_handler(get_profile_handler())
    register_weather_handlers(app)
    register_nearby_handlers(app)
    register_language_handlers(app)
    register_menu_handlers(app)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message_handler))
    app.add_error_handler(global_error_handler)

    logger.info("Sayohatchi Bot is starting polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
`
  }
];
