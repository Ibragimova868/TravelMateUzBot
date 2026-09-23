"""
English language dictionary for Sayohatchi Bot.
"""

MESSAGES = {
    # General & Navigation
    "btn_back": "🔙 Back",
    "btn_cancel": "❌ Cancel",
    "cancelled": "Operation cancelled. You are back in the main menu.",
    "unknown_command": "Unknown command or message. Please use the menu buttons below.",
    "service_error": "Service is temporarily unavailable. Please try again later.",
    "input_too_long": "Entered text is too long. Please keep it brief (maximum 100 characters).",
    "invalid_input": "Invalid input provided. Please try again.",

    # Start & Registration
    "welcome_new_user": "Welcome! Hello!",
    "choose_language_prompt": "Please choose your preferred language:\nIltimos, o‘zingizga qulay tilni tanlang:\nПожалуйста, выберите удобный язык:",
    "ask_first_name": "Please enter your first name:",
    "ask_last_name": "Please enter your last name:",
    "registration_success": "Congratulations, {name}! You have registered successfully.\nChoose a service from the menu below:",
    "welcome_back": "Welcome back, {name}!\nChoose a service from the menu below:",

    # Main Menu buttons
    "menu_title": "Main Menu:",
    "btn_distance_route": "📍 Distance & Travel Time",
    "btn_weather": "🌤️ 7-Day Weather Forecast",
    "btn_nearby": "📍 Find Nearby Places",
    "btn_profile": "👤 My Profile",
    "btn_change_language": "🌐 Change Language",
    "btn_about": "ℹ️ About Bot",

    # Routing
    "route_ask_origin": "Where are you departing from?\n(Enter city/address or coordinates, e.g. Bukhara or 39.7747, 64.4286)",
    "route_ask_destination": "Where are you travelling to?\n(Enter city/address or coordinates, e.g. Samarkand or 41.2995, 69.2401)",
    "route_select_transport": "Select transport mode:",
    "transport_walk": "🚶 Walking",
    "transport_bike": "🚲 Cycling",
    "transport_moto": "🏍️ Motorcycle",
    "transport_car": "🚗 Driving (Car)",
    "route_calculating": "Calculating road route and travel duration, please wait...",
    "route_result_header": "🚗 Route Calculation Result:",
    "route_origin_label": "📍 Origin:\n{origin}",
    "route_destination_label": "🏁 Destination:\n{destination}",
    "route_transport_label": "🚗 Mode of Transport:\n{transport}",
    "route_distance_label": "📏 Distance:\n{distance}",
    "route_duration_label": "⏱ Travel time:\n{duration}",
    "route_address_not_found": "Sorry, address '{query}' could not be found. Please check spelling or be more specific.",
    "invalid_coordinates": "Invalid coordinates. Please use this format:\n39.7747, 64.4286\n(Latitude: -90 to 90, Longitude: -180 to 180)",
    "route_calc_error": "Route information could not be calculated. Please try again later.",
    "route_api_missing": "OpenRouteService API key is not configured. Please contact the bot administrator.",

    # Weather
    "weather_select_region": "Which region's weather would you like to see?\nSelect a region:",
    "weather_header": "🌤️ {region} — 7-Day Weather Forecast\n",
    "weather_day_format": "📅 {day_name}\n{icon} {temp_max}°C / {temp_min}°C\n💨 Wind: {wind} km/h\n💧 Precipitation probability: {rain}%\n",
    "weather_error": "Failed to retrieve weather data. Please try again in a few moments.",

    # Nearby Places
    "nearby_send_location_prompt": "To find nearby places, please share your location using the button below:",
    "btn_send_location": "📍 Share Location",
    "nearby_location_received": "Location received successfully!\nWhat category of places are you looking for?",
    "nearby_pharmacy": "🏥 Pharmacies",
    "nearby_cafe": "🍽 Cafes & Restaurants",
    "nearby_hotel": "🏨 Hotels",
    "nearby_fuel": "⛽ Gas Stations",
    "nearby_bank": "🏦 Banks & ATMs",
    "nearby_shop": "🏪 Stores & Supermarkets",
    "nearby_searching": "Searching for nearby {category}...",
    "nearby_result_header": "📍 Nearby {category} (sorted by closest distance):\n",
    "nearby_item_format": "{index}. {name}\n📍 Address: {address}\n📏 Distance: {distance}\n",
    "nearby_not_found": "No {category} found within a 5 km radius.",
    "nearby_error": "An error occurred while searching for nearby places. Please try again later.",

    # Profile
    "profile_title": "👤 Profile\n\nFirst Name: {first_name}\nLast Name: {last_name}\n🌐 Language: {language}\n📅 Registration date: {created_at}",
    "btn_edit_name": "✏️ Edit Name",
    "ask_new_first_name": "Enter your new first name:",
    "ask_new_last_name": "Enter your new last name:",
    "name_updated_success": "Your name has been updated successfully!",

    # Language Change
    "choose_new_language": "Select a new language / Yangi tilni tanlang / Выберите новый язык:",
    "language_updated": "Language successfully changed to: 🇬🇧 English",

    # About
    "about_text": (
        "ℹ️ About Sayohatchi Bot:\n\n"
        "Your intelligent companion for travel, navigation, and everyday exploration across Uzbekistan:\n\n"
        "🛣️ Real road distance and travel time calculation for driving, cycling, and walking\n"
        "🌤️ 7-day weather forecast for all 13 regions of Uzbekistan\n"
        "📍 Instant search for nearby pharmacies, cafes, hotels, gas stations, banks, and supermarkets\n"
        "🌐 Full trilingual support: Uzbek, Russian, and English\n\n"
        "Version: 2.0.0 (Production-Ready)\n"
        "Powered by: Python 3.11+, python-telegram-bot, OpenRouteService, Open-Meteo, OpenStreetMap Overpass"
    ),

    # Weekday names
    "weekdays": {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    },

    # Weather descriptions
    "weather_desc": {
        "clear": "Clear sky",
        "partly_cloudy": "Partly cloudy",
        "cloudy": "Cloudy",
        "overcast": "Overcast",
        "fog": "Fog",
        "drizzle": "Drizzle",
        "rain": "Rain",
        "heavy_rain": "Heavy rain",
        "snow": "Snow",
        "thunderstorm": "Thunderstorm",
    },
}
