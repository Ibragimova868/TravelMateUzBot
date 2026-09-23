"""
Uzbek language dictionary for Sayohatchi Bot.
"""

MESSAGES = {
    # General & Navigation
    "btn_back": "🔙 Orqaga",
    "btn_cancel": "❌ Bekor qilish",
    "cancelled": "Jarayon bekor qilindi. Bosh menyudasiz.",
    "unknown_command": "Noma'lum buyruq yoki xabar. Iltimos, menyudagi tugmalardan foydalaning.",
    "service_error": "Xizmat vaqtincha ishlamayapti. Keyinroq qayta urinib ko‘ring.",
    "input_too_long": "Kiritilgan matn juda uzun. Iltimos, qisqaroq qilib qayta yozing (maksimal 100 ta belgi).",
    "invalid_input": "Noto‘g‘ri ma'lumot kiritildi. Iltimos, qaytadan urinib ko‘ring.",

    # Start & Registration
    "welcome_new_user": "Assalomu alaykum. Xush kelibsiz!",
    "choose_language_prompt": "Iltimos, o‘zingizga qulay tilni tanlang:\nПожалуйста, выберите удобный язык:\nPlease choose your preferred language:",
    "ask_first_name": "Ismingizni kiriting:",
    "ask_last_name": "Familiyangizni kiriting:",
    "registration_success": "Tabriklaymiz, {name}! Ro‘yxatdan muvaffaqiyatli o‘tdingiz.\nQuyidagi menyudan kerakli xizmatni tanlang:",
    "welcome_back": "Qaytganingiz bilan, {name}!\nQuyidagi menyudan kerakli xizmatni tanlang:",

    # Main Menu buttons
    "menu_title": "Bosh menyu:",
    "btn_distance_route": "📍 Masofa va yo‘l vaqti",
    "btn_weather": "🌤️ 1 haftalik ob-havo",
    "btn_nearby": "📍 Yaqin joylarni topish",
    "btn_profile": "👤 Profilim",
    "btn_change_language": "🌐 Tilni o‘zgartirish",
    "btn_about": "ℹ️ Bot haqida",

    # Routing
    "route_ask_origin": "Qayerdan ketasiz?\n(Shahar/manzil nomini yoki koordinatalarni kiriting, masalan: Toshkent yoki 39.7747, 64.4286)",
    "route_ask_destination": "Qayerga borasiz?\n(Boriladigan shahar/manzil nomini yoki koordinatalarni kiriting, masalan: Samarqand yoki 41.2995, 69.2401)",
    "route_select_transport": "Transport turini tanlang:",
    "transport_walk": "🚶 Piyoda",
    "transport_bike": "🚲 Velosiped",
    "transport_moto": "🏍️ Mototsikl",
    "transport_car": "🚗 Avtomobil",
    "route_calculating": "Yo‘nalish va masofa hisoblanmoqda, iltimos kuting...",
    "route_result_header": "🚗 Marshrut hisob-kitobi natijasi:",
    "route_origin_label": "📍 Boshlang‘ich manzil:\n{origin}",
    "route_destination_label": "🏁 Boriladigan manzil:\n{destination}",
    "route_transport_label": "🚗 Transport:\n{transport}",
    "route_distance_label": "📏 Masofa:\n{distance}",
    "route_duration_label": "⏱ Yo‘l vaqti:\n{duration}",
    "route_address_not_found": "Kechirasiz, '{query}' manzili topilmadi. Iltimos, manzil nomini to‘g‘riroq yoki kengroq qilib yozing.",
    "invalid_coordinates": "Noto‘g‘ri koordinata kiritildi. Iltimos, quyidagi formatda kiriting:\n39.7747, 64.4286\n(Kenglik: -90 dan 90 gacha, Uzunlik: -180 dan 180 gacha)",
    "route_calc_error": "Yo‘nalish ma'lumotlarini hisoblab bo‘lmadi. Iltimos, keyinroq qayta urinib ko‘ring.",
    "route_api_missing": "Yo‘nalish xizmati API kaliti sozlanmagan. Iltimos, bot ma'muriga murojaat qiling.",

    # Weather
    "weather_select_region": "Qaysi viloyat ob-havosini bilmoqchisiz?\nViloyatni tanlang:",
    "weather_header": "🌤️ {region} — 7 kunlik ob-havo\n",
    "weather_day_format": "📅 {day_name}\n{icon} {temp_max}°C / {temp_min}°C\n💨 Shamol: {wind} km/soat\n💧 Yog‘ingarchilik ehtimoli: {rain}%\n",
    "weather_error": "Ob-havo ma'lumotlarini olishda xatolik yuz berdi. Iltimos, birozdan so‘ng qayta urinib ko‘ring.",

    # Nearby Places
    "nearby_send_location_prompt": "Yaqin joylarni topish uchun, iltimos, pastdagi tugma orqali joylashuvingizni (geolokatsiya) yuboring:",
    "btn_send_location": "📍 Joylashuvni yuborish",
    "nearby_location_received": "Joylashuvingiz qabul qilindi!\nQanday joylarni qidirmoqchisiz?",
    "nearby_pharmacy": "🏥 Dorixonalar",
    "nearby_cafe": "🍽 Kafelar",
    "nearby_hotel": "🏨 Mehmonxonalar",
    "nearby_fuel": "⛽ Yoqilg‘i shoxobchalari",
    "nearby_bank": "🏦 Banklar",
    "nearby_shop": "🏪 Do‘konlar",
    "nearby_searching": "Yaqin-atrofdagi {category} qidirilmoqda...",
    "nearby_result_header": "📍 Yaqin-atrofdagi {category} ro‘yxati (eng yaqinlari):\n",
    "nearby_item_format": "{index}. {name}\n📍 Manzil: {address}\n📏 Masofa: {distance}\n",
    "nearby_not_found": "Afsuski, 5 km radiusda birorta ham {category} topilmadi.",
    "nearby_error": "Yaqin joylarni qidirishda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko‘ring.",

    # Profile
    "profile_title": "👤 Profilim\n\nIsm: {first_name}\nFamiliya: {last_name}\n🌐 Til: {language}\n📅 Ro‘yxatdan o‘tgan sana: {created_at}",
    "btn_edit_name": "✏️ Ismni o‘zgartirish",
    "ask_new_first_name": "Yangi ismingizni kiriting:",
    "ask_new_last_name": "Yangi familiyangizni kiriting:",
    "name_updated_success": "Ism va familiyangiz muvaffaqiyatli yangilandi!",

    # Language Change
    "choose_new_language": "Yangi tilni tanlang / Выберите новый язык / Select a new language:",
    "language_updated": "Til muvaffaqiyatli o‘zgartirildi: 🇺🇿 O‘zbek",

    # About
    "about_text": (
        "ℹ️ Sayohatchi Bot haqida:\n\n"
        "Ushbu bot sayohat, navigatsiya va kundalik ehtiyojlar uchun sizga yordam beradi:\n\n"
        "🛣️ Avtomobil, velosiped va piyoda yo‘llari bo‘yicha aniq masofa va vaqtni hisoblash\n"
        "🌤️ O‘zbekistonning barcha 13 viloyati bo‘yicha 7 kunlik ob-havo ma'lumoti\n"
        "📍 Joylashuvingizga qarab eng yaqin dorixona, kafe, mehmonxona, zapravka va do‘konlarni topish\n"
        "🌐 O‘zbek, rus va ingliz tillarida to‘liq xizmat ko‘rsatish\n\n"
        "Versiya: 2.0.0 (Production-Ready)\n"
        "Texnologiyalar: Python 3.11+, python-telegram-bot, OpenRouteService, Open-Meteo, OpenStreetMap Overpass"
    ),

    # Weekday names
    "weekdays": {
        0: "Dushanba",
        1: "Seshanba",
        2: "Chorshanba",
        3: "Payshanba",
        4: "Juma",
        5: "Shanba",
        6: "Yakshanba",
    },

    # Weather descriptions
    "weather_desc": {
        "clear": "Ochiq havo",
        "partly_cloudy": "Biroz bulutli",
        "cloudy": "Bulutli",
        "overcast": "Qalin bulutli",
        "fog": "Tumanli",
        "drizzle": "Mayda yomg‘ir",
        "rain": "Yomg‘ir",
        "heavy_rain": "Kuchli yomg‘ir",
        "snow": "Qor",
        "thunderstorm": "Momaqaldiroq",
    },
}
