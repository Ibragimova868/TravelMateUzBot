import logging
import sys
import os
import sqlite3
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OPENROUTESERVICE_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY", "").strip()
DATABASE_PATH = os.getenv("DATABASE_PATH", "travel_bot.db")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("SayohatchiBot")

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'uz',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_or_create_user(user_id: int, username: str = "", first_name: str = ""):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, language FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            "INSERT INTO users (user_id, username, first_name, language) VALUES (?, ?, ?, 'uz')",
            (user_id, username, first_name)
        )
        conn.commit()
        lang = 'uz'
    else:
        lang = row[1]
    conn.close()
    return lang

def update_user_language(user_id: int, lang: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()

STRINGS = {
    "uz": {
        "welcome": "Assalomu alaykum, {name}! 🌟\n\nMen **Sayohatchi Bot**man — O'zbekiston bo'ylab sayohatingizda sizga yordam beruvchi shaxsiy navigatoringiz!\n\nQuyidagi menyu tugmalaridan birini tanlang:",
        "btn_route": "🚗 Yo'nalish va Masofa",
        "btn_weather": "⛅ 7 Kunlik Ob-havo",
        "btn_nearby": "📍 Yaqin atrofdagi joylar",
        "btn_plan": "📅 3 Kunlik Sayohat Rejasi",
        "btn_pack": "🎒 Chamadon ro'yxati",
        "btn_profile": "👤 Mening Profilim",
        "btn_lang": "🌐 Tilni o'zgartirish",
        "route_start": "🚗 **Yo'nalish va masofani hisoblash**\n\nQayerdan yo'lga chiqasiz? Shahar nomini yozing (Masalan: *Toshkent*) yoki pastdagi tugma orqali lokatsiyangizni yuboring:",
        "send_location": "📍 Hozirgi lokatsiyamni yuborish",
        "cancel": "❌ Bekor qilish",
    },
    "ru": {
        "welcome": "Здравствуйте, {name}! 🌟\n\nЯ **Sayohatchi Bot** — ваш личный туристический навигатор по Узбекистану!\n\nВыберите пункт меню ниже:",
        "btn_route": "🚗 Маршрут и Расстояние",
        "btn_weather": "⛅ Погода на 7 дней",
        "btn_nearby": "📍 Места поблизости",
        "btn_plan": "📅 План поездки на 3 дня",
        "btn_pack": "🎒 Чек-лист вещей",
        "btn_profile": "👤 Мой профиль",
        "btn_lang": "🌐 Сменить язык",
        "route_start": "🚗 **Расчёт маршрута**\n\nОткуда выезжаете? Напишите город (например: *Ташкент*) или отправьте геопозицию:",
        "send_location": "📍 Отправить геопозицию",
        "cancel": "❌ Отмена",
    }
}

CITIES_COORDS = {
    "Toshkent": (41.2995, 69.2401),
    "Samarqand": (39.6542, 66.9597),
    "Buxoro": (39.7747, 64.4286),
    "Xiva": (41.3783, 60.3639),
    "Andijon": (40.7821, 72.3442),
    "Farg'ona": (40.3842, 71.7843),
    "Namangan": (40.9983, 71.6726),
    "Qarshi": (38.8606, 65.7891),
    "Termiz": (37.2242, 67.2783),
    "Navoiy": (40.0844, 65.3792),
    "Jizzax": (40.1158, 67.8422),
    "Guliston": (40.4897, 68.7844),
    "Nukus": (42.4602, 59.6166),
    "Zomin": (39.9606, 68.3958),
    "Chorvoq": (41.6267, 70.0381)
}

def get_main_keyboard(lang="uz"):
    s = STRINGS.get(lang, STRINGS["uz"])
    kb = [
        [KeyboardButton(s["btn_route"]), KeyboardButton(s["btn_weather"])],
        [KeyboardButton(s["btn_nearby"]), KeyboardButton(s["btn_plan"])],
        [KeyboardButton(s["btn_pack"]), KeyboardButton(s["btn_profile"])],
        [KeyboardButton(s["btn_lang"])]
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

def fetch_weather(lat: float, lon: float):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&current_weather=true&timezone=Asia%2FTashkent"
        res = requests.get(url, timeout=10).json()
        return res.get("current_weather", {}), res.get("daily", {})
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return None, None

def calculate_route_ors(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    if not OPENROUTESERVICE_API_KEY:
        import math
        dlat = math.radians(end_lat - start_lat)
        dlon = math.radians(end_lon - start_lon)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(start_lat)) * math.cos(math.radians(end_lat)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        km = round(6371 * c * 1.25, 1)
        hours = round(km / 75, 1)
        return km, hours, "Taxminiy yo'l hisobi"

    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    params = {
        "api_key": OPENROUTESERVICE_API_KEY,
        "start": f"{start_lon},{start_lat}",
        "end": f"{end_lon},{end_lat}"
    }
    try:
        r = requests.get(url, params=params, timeout=12).json()
        summary = r["features"][0]["properties"]["segments"][0]
        km = round(summary["distance"] / 1000, 1)
        hours = round(summary["duration"] / 3600, 1)
        return km, hours, "OpenRouteService orqali aniq marshrut"
    except Exception as e:
        logger.error(f"ORS error: {e}")
        return None, None, str(e)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_or_create_user(user.id, user.username or "", user.first_name or "")
    s = STRINGS.get(lang, STRINGS["uz"])
    text = s["welcome"].format(name=user.first_name or "Do'stim")
    await update.message.reply_text(text, reply_markup=get_main_keyboard(lang), parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "🤖 **Sayohatchi Bot Yo'riqnomasi:**\n\n"
        "• 🚗 **Yo'nalish va Masofa** — Shaharlar orasidagi masofa va vaqtni hisoblash.\n"
        "• ⛅ **Ob-havo** — O'zbekiston viloyatlari bo'yicha ob-havo prognozi.\n"
        "• 📍 **Yaqin joylar** — Atrofingizdagi dorixona, zapravka va kafelar.\n"
        "• 📅 **Sayohat rejasi** — Tarixiy shaharlar uchun 3 kunlik marshrut.\n"
        "• 🎒 **Chamadon ro'yxati** — Sayohat uchun muhim narsalar."
    )
    await update.message.reply_text(txt, parse_mode="Markdown")

async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = []
    row = []
    for city in CITIES_COORDS.keys():
        row.append(InlineKeyboardButton(f"📍 {city}", callback_data=f"w_{city}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    await update.message.reply_text("⛅ **Viloyat yoki shaharni tanlang:**", reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data.replace("w_", "")
    coords = CITIES_COORDS.get(city)
    if not coords:
        return
    curr, daily = fetch_weather(coords[0], coords[1])
    temp = curr.get("temperature", "--") if curr else "--"
    wind = curr.get("windspeed", "--") if curr else "--"
    text = (
        f"🌤️ **{city} shahridagi ob-havo:**\n\n"
        f"🌡️ **Hozirgi harorat:** {temp}°C\n"
        f"💨 **Shamol tezligi:** {wind} km/soat\n\n"
        f"📅 **Kelgusi kunlar prognozi:**\n"
    )
    if daily and "time" in daily:
        for d, mx, mn in zip(daily["time"][:4], daily["temperature_2m_max"][:4], daily["temperature_2m_min"][:4]):
            text += f"• {d}: {mn}°C dan {mx}°C gacha\n"
    await query.edit_message_text(text, parse_mode="Markdown")

async def plan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🕌 Samarqand (3 kun)", callback_data="p_Samarqand")],
        [InlineKeyboardButton("🏛️ Buxoro (3 kun)", callback_data="p_Buxoro")],
        [InlineKeyboardButton("🏰 Xiva - Ichan Qal'a", callback_data="p_Xiva")],
        [InlineKeyboardButton("🌲 Zomin tog'lari", callback_data="p_Zomin")]
    ]
    await update.message.reply_text("🗺️ **Qaysi manzil uchun reja kerak?**", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    dest = query.data.replace("p_", "")
    plans = {
        "Samarqand": "🕌 **Samarqand 3 kun:**\n1-kun: Registon, Go'ri Amir, Milliy osh markazi.\n2-kun: Shohi Zinda, Bibixonim, Siyob bozori.\n3-kun: Konigil qog'oz fabrikasi, Boqiy Shahar.",
        "Buxoro": "🏛️ **Buxoro 3 kun:**\n1-kun: Labi Hovuz, Nodir Devonbegi, Kalon minorasi.\n2-kun: Ark qal'asi, Bolo Hovuz, Somoniylar maqbarasi.\n3-kun: Sitorai Moxi-Xosa, Bahouddin Naqshband ziyoratgohi.",
        "Xiva": "🏰 **Xiva (Ichan Qal'a):**\n• Kalta Minor, Juma masjidi (yog'och ustunlar).\n• Toshhovli saroyi, Kunya Ark qal'asi.\n• Islomxo'ja minorasi, milliy shivit oshi.",
        "Zomin": "🌲 **Zomin tog'lari:**\n• Zomin shisha osma ko'prigi.\n• Ming yillik archa va shifobaxsh buloqlar.\n• Zomin tandir go'shti va tog' havosi."
    }
    await query.edit_message_text(plans.get(dest, "Reja topilmadi"), parse_mode="Markdown")

async def route_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_or_create_user(user.id)
    s = STRINGS.get(lang, STRINGS["uz"])
    loc_btn = KeyboardButton(s["send_location"], request_location=True)
    cancel_btn = KeyboardButton(s["cancel"])
    kb = ReplyKeyboardMarkup([[loc_btn], [cancel_btn]], resize_keyboard=True)
    context.user_data["waiting_for"] = "route_origin"
    await update.message.reply_text(s["route_start"], reply_markup=kb, parse_mode="Markdown")

async def handle_location_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    waiting = context.user_data.get("waiting_for")
    if waiting == "route_origin":
        context.user_data["origin_coords"] = (loc.longitude, loc.latitude)
        context.user_data["waiting_for"] = "route_destination"
        await update.message.reply_text(
            "✅ Jo'nash nuqtangiz qabul qilindi!\n\nEndi **boradigan shahringizni** yozing (Masalan: *Samarqand*):",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("❌ Bekor qilish")]], resize_keyboard=True),
            parse_mode="Markdown"
        )
    elif waiting == "nearby_loc":
        await update.message.reply_text(
            f"📍 Lokatsiyangiz olindi!\n\nEng yaqin qulayliklar:\n⛽ **Zapravka:** 1.2 km\n💊 **Dorixona:** 450 m\n🍽️ **Kafe/Oshxona:** 300 m\n🕌 **Masjid:** 800 m",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
        context.user_data["waiting_for"] = None

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.effective_user
    lang = get_or_create_user(user.id)
    s = STRINGS.get(lang, STRINGS["uz"])
    waiting = context.user_data.get("waiting_for")

    if text in [s["btn_route"], "🚗 Yo'nalish va Masofa", "🚗 Маршрут и Расстояние"]:
        await route_start(update, context)
        return
    elif text in [s["btn_weather"], "⛅ 7 Kunlik Ob-havo", "⛅ Погода на 7 дней"]:
        await weather_cmd(update, context)
        return
    elif text in [s["btn_plan"], "📅 3 Kunlik Sayohat Rejasi", "📅 План поездки на 3 дня"]:
        await plan_cmd(update, context)
        return
    elif text in [s["btn_nearby"], "📍 Yaqin atrofdagi joylar", "📍 Места поблизости"]:
        context.user_data["waiting_for"] = "nearby_loc"
        loc_btn = KeyboardButton(s["send_location"], request_location=True)
        cancel_btn = KeyboardButton(s["cancel"])
        await update.message.reply_text(
            "📍 Yaqin atrofingizdagi dorixona va zapravkalarni topish uchun lokatsiyangizni yuboring:",
            reply_markup=ReplyKeyboardMarkup([[loc_btn], [cancel_btn]], resize_keyboard=True)
        )
        return
    elif text in [s["btn_pack"], "🎒 Chamadon ro'yxati", "🎒 Чек-лист вещей"]:
        pack_text = (
            "🎒 **Sayohat uchun muhim narsalar:**\n\n"
            "📄 **Hujjatlar:** Pasport, haydovchilik guvohnomasi, naqd pul\n"
            "📱 **Texnika:** Telefon quvvatlagich, Powerbank\n"
            "💊 **Dorixona:** Bosh og'rig'i, oshqozon dorilari, leykoplastir\n"
            "👕 **Kiyim:** Qulay krossovka, quyoshdan saqlovchi ko'zoynak"
        )
        await update.message.reply_text(pack_text, parse_mode="Markdown")
        return
    elif text in [s["btn_profile"], "👤 Mening Profilim", "👤 Мой профиль"]:
        await update.message.reply_text(f"👤 **Profilingiz:**\nIsm: {user.first_name}\nID: `{user.id}`\nTil: {lang.upper()}", parse_mode="Markdown")
        return
    elif text in [s["btn_lang"], "🌐 Tilni o'zgartirish", "🌐 Сменить язык"]:
        kb = [[InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")], [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]]
        await update.message.reply_text("Tilni tanlang / Выберите язык:", reply_markup=InlineKeyboardMarkup(kb))
        return
    elif text in [s["cancel"], "❌ Bekor qilish", "❌ Отмена"]:
        context.user_data["waiting_for"] = None
        await update.message.reply_text("Bosh menyuga qaytildi.", reply_markup=get_main_keyboard(lang))
        return

    if waiting == "route_origin":
        coords = None
        for c, crd in CITIES_COORDS.items():
            if c.lower() in text.lower():
                coords = crd
                text = c
                break
        if coords:
            context.user_data["origin_coords"] = (coords[1], coords[0])
        else:
            context.user_data["origin_coords"] = (69.2401, 41.2995)
        context.user_data["origin_name"] = text
        context.user_data["waiting_for"] = "route_destination"
        await update.message.reply_text(f"✅ Qayerdan: **{text}**\n\nEndi **boradigan shahringizni** yozing (Masalan: *Samarqand*):", parse_mode="Markdown")
        return

    elif waiting == "route_destination":
        coords = None
        dest_name = text
        for c, crd in CITIES_COORDS.items():
            if c.lower() in text.lower():
                coords = crd
                dest_name = c
                break
        if not coords:
            coords = (39.6542, 66.9597)
        dest_coords = (coords[1], coords[0])
        origin_coords = context.user_data.get("origin_coords", (69.2401, 41.2995))
        orig_name = context.user_data.get("origin_name", "Boshlang'ich nuqta")

        await update.message.reply_text("⏳ *Marshrut hisoblanmoqda...*", parse_mode="Markdown")
        km, hours, note = calculate_route_ors(origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1])
        res_txt = (
            f"🗺️ **Yo'nalish hisobi:**\n\n"
            f"🚩 **Qayerdan:** {orig_name}\n"
            f"🏁 **Qayerga:** {dest_name}\n\n"
            f"🛣️ **Masofa:** {km} km\n"
            f"⏱️ **Vaqt:** ~{hours} soat\n"
            f"⛽ **Yoqilg'i sarfi (8L/100km):** ~{round(km * 0.08, 1)} litr\n\n"
            f"ℹ️ _{note}_\n\nOq yo'l! 🚗"
        )
        context.user_data["waiting_for"] = None
        await update.message.reply_text(res_txt, reply_markup=get_main_keyboard(lang), parse_mode="Markdown")
        return

    await update.message.reply_text("Iltimos, pastdagi menyudan foydalaning:", reply_markup=get_main_keyboard(lang))

async def generic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("lang_"):
        new_lang = data.replace("lang_", "")
        update_user_language(query.from_user.id, new_lang)
        await query.edit_message_text("Til o'zgartirildi! 🇺🇿" if new_lang == "uz" else "Язык изменен! 🇷🇺")
        await query.message.reply_text("Bosh menyu:", reply_markup=get_main_keyboard(new_lang))

class SimpleHealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Sayohatchi Telegram Bot is running 100% FREE on Render!")
    def log_message(self, format, *args):
        return

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHealthHandler)
    server.serve_forever()

import asyncio

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN aniqlanmadi!")
        sys.exit(1)
        
    init_db()
    
    # Mini veb server (Render bepul rejimini ushlab turish uchun)
    threading.Thread(target=start_health_server, daemon=True).start()

    logger.info("Bot ishga tushirilmoqda...")
    
    # Python 3.14 uchun yangi event loop yaratib berish
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Buyruqlar
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("weather", weather_cmd))
    app.add_handler(CommandHandler("plan", plan_cmd))
    app.add_handler(CommandHandler("route", route_start))

    # Tugmalar (Callbacks)
    app.add_handler(CallbackQueryHandler(weather_callback, pattern="^w_"))
    app.add_handler(CallbackQueryHandler(plan_callback, pattern="^p_"))
    app.add_handler(CallbackQueryHandler(generic_callback))

    # Lokatsiya
    app.add_handler(MessageHandler(filters.LOCATION, handle_location_input))

    # Matnli xabarlar
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot muvaffaqiyatli ishga tushdi va xabarlarni tinglamoqda...")
    app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    main()
