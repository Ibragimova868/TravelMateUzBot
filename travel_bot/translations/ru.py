"""
Russian language dictionary for Sayohatchi Bot.
"""

MESSAGES = {
    # General & Navigation
    "btn_back": "🔙 Назад",
    "btn_cancel": "❌ Отмена",
    "cancelled": "Действие отменено. Вы в главном меню.",
    "unknown_command": "Неизвестная команда или сообщение. Пожалуйста, используйте кнопки меню.",
    "service_error": "Сервис временно недоступен. Пожалуйста, попробуйте позже.",
    "input_too_long": "Введённый текст слишком длинный. Пожалуйста, напишите короче (максимум 100 символов).",
    "invalid_input": "Введены некорректные данные. Пожалуйста, попробуйте снова.",

    # Start & Registration
    "welcome_new_user": "Здравствуйте. Добро пожаловать!",
    "choose_language_prompt": "Пожалуйста, выберите удобный язык:\nIltimos, o‘zingizga qulay tilni tanlang:\nPlease choose your preferred language:",
    "ask_first_name": "Введите ваше имя:",
    "ask_last_name": "Введите вашу фамилию:",
    "registration_success": "Поздравляем, {name}! Вы успешно зарегистрированы.\nВыберите нужную услугу из меню ниже:",
    "welcome_back": "С возвращением, {name}!\nВыберите нужную услугу из меню ниже:",

    # Main Menu buttons
    "menu_title": "Главное меню:",
    "btn_distance_route": "📍 Расстояние и время в пути",
    "btn_weather": "🌤️ Погода на 7 дней",
    "btn_nearby": "📍 Поиск мест поблизости",
    "btn_profile": "👤 Мой профиль",
    "btn_change_language": "🌐 Изменить язык",
    "btn_about": "ℹ️ О боте",

    # Routing
    "route_ask_origin": "Откуда вы выезжаете?\n(Введите город/адрес или координаты, например: Бухара или 39.7747, 64.4286)",
    "route_ask_destination": "Куда вы направляетесь?\n(Введите город/адрес или координаты, например: Самарканд или 41.2995, 69.2401)",
    "route_select_transport": "Выберите вид транспорта:",
    "transport_walk": "🚶 Пешком",
    "transport_bike": "🚲 Велосипед",
    "transport_moto": "🏍️ Мотоцикл",
    "transport_car": "🚗 Автомобиль",
    "route_calculating": "Рассчитываем маршрут и расстояние, пожалуйста, подождите...",
    "route_result_header": "🚗 Результат расчёта маршрута:",
    "route_origin_label": "📍 Начальная точка:\n{origin}",
    "route_destination_label": "🏁 Пункт назначения:\n{destination}",
    "route_transport_label": "🚗 Транспорт:\n{transport}",
    "route_distance_label": "📏 Расстояние:\n{distance}",
    "route_duration_label": "⏱ Время в пути:\n{duration}",
    "route_address_not_found": "К сожалению, адрес '{query}' не найден. Пожалуйста, уточните название города или улицы.",
    "invalid_coordinates": "Неверные координаты. Пожалуйста, используйте следующий формат:\n39.7747, 64.4286\n(Широта: от -90 до 90, Долгота: от -180 до 180)",
    "route_calc_error": "Не удалось рассчитать информацию о маршруте. Пожалуйста, повторите попытку позже.",
    "route_api_missing": "API ключ службы маршрутизации не настроен. Обратитесь к администратору бота.",

    # Weather
    "weather_select_region": "Погоду какого региона вы хотите узнать?\nВыберите регион:",
    "weather_header": "🌤️ {region} — прогноз погоды на 7 дней\n",
    "weather_day_format": "📅 {day_name}\n{icon} {temp_max}°C / {temp_min}°C\n💨 Ветер: {wind} км/ч\n💧 Вероятность осадков: {rain}%\n",
    "weather_error": "Произошла ошибка при получении данных о погоде. Пожалуйста, попробуйте позже.",

    # Nearby Places
    "nearby_send_location_prompt": "Чтобы найти места поблизости, пожалуйста, отправьте вашу геолокацию кнопкой ниже:",
    "btn_send_location": "📍 Отправить локацию",
    "nearby_location_received": "Ваша геолокация получена!\nЧто именно вы хотите найти поблизости?",
    "nearby_pharmacy": "🏥 Аптеки",
    "nearby_cafe": "🍽 Кафе и рестораны",
    "nearby_hotel": "🏨 Отели",
    "nearby_fuel": "⛽ Заправки (АЗС)",
    "nearby_bank": "🏦 Банки и банкоматы",
    "nearby_shop": "🏪 Магазины",
    "nearby_searching": "Ищем {category} поблизости...",
    "nearby_result_header": "📍 Список мест поблизости ({category}):\n",
    "nearby_item_format": "{index}. {name}\n📍 Адрес: {address}\n📏 Расстояние: {distance}\n",
    "nearby_not_found": "К сожалению, в радиусе 5 км ничего не найдено ({category}).",
    "nearby_error": "Произошла ошибка при поиске мест поблизости. Пожалуйста, попробуйте позже.",

    # Profile
    "profile_title": "👤 Профиль\n\nИмя: {first_name}\nФамилия: {last_name}\n🌐 Язык: {language}\n📅 Дата регистрации: {created_at}",
    "btn_edit_name": "✏️ Изменить имя",
    "ask_new_first_name": "Введите новое имя:",
    "ask_new_last_name": "Введите новую фамилию:",
    "name_updated_success": "Имя и фамилия успешно обновлены!",

    # Language Change
    "choose_new_language": "Выберите новый язык / Yangi tilni tanlang / Select a new language:",
    "language_updated": "Язык успешно изменён на: 🇷🇺 Русский",

    # About
    "about_text": (
        "ℹ️ О боте Sayohatchi:\n\n"
        "Этот бот — ваш надёжный помощник в путешествиях, навигации и повседневной жизни:\n\n"
        "🛣️ Точный расчёт дорожного расстояния и времени в пути на авто, велосипеде и пешком\n"
        "🌤️ Прогноз погоды на 7 дней по всем 13 регионам Узбекистана\n"
        "📍 Быстрый поиск ближайших аптек, кафе, отелей, АЗС, банков и магазинов по геолокации\n"
        "🌐 Полная поддержка трёх языков: узбекский, русский и английский\n\n"
        "Версия: 2.0.0 (Production-Ready)\n"
        "Технологии: Python 3.11+, python-telegram-bot, OpenRouteService, Open-Meteo, OpenStreetMap Overpass"
    ),

    # Weekday names
    "weekdays": {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье",
    },

    # Weather descriptions
    "weather_desc": {
        "clear": "Ясно",
        "partly_cloudy": "Малооблачно",
        "cloudy": "Переменная облачность",
        "overcast": "Пасмурно",
        "fog": "Туман",
        "drizzle": "Морось",
        "rain": "Дождь",
        "heavy_rain": "Ливень",
        "snow": "Снег",
        "thunderstorm": "Гроза",
    },
}
