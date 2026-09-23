"""
Weather forecast service for Sayohatchi Bot.
Fetches 7-day weather forecasts for Uzbekistan regions using Open-Meteo API.
Converts WMO weather codes to emojis and localized descriptions.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from config import HTTP_TIMEOUT
from services.http_client import http_get
from translations import t, get_weekday_name, get_weather_desc

logger = logging.getLogger(__name__)

# WMO Weather Interpretation Codes mapping: code -> (icon, desc_key)
WMO_WEATHER_CODES = {
    0: ("☀️", "clear"),
    1: ("🌤️", "partly_cloudy"),
    2: ("⛅", "cloudy"),
    3: ("☁️", "overcast"),
    45: ("🌫️", "fog"),
    48: ("🌫️", "fog"),
    51: ("🌦️", "drizzle"),
    53: ("🌦️", "drizzle"),
    55: ("🌦️", "drizzle"),
    56: ("🌨️", "drizzle"),
    57: ("🌨️", "drizzle"),
    61: ("🌧️", "rain"),
    63: ("🌧️", "rain"),
    65: ("🌧️", "heavy_rain"),
    66: ("🌧️", "rain"),
    67: ("🌧️", "heavy_rain"),
    71: ("🌨️", "snow"),
    73: ("🌨️", "snow"),
    75: ("🌨️", "snow"),
    77: ("🌨️", "snow"),
    80: ("🌧️", "rain"),
    81: ("🌧️", "rain"),
    82: ("🌧️", "heavy_rain"),
    85: ("🌨️", "snow"),
    86: ("🌨️", "snow"),
    95: ("⛈️", "thunderstorm"),
    96: ("⛈️", "thunderstorm"),
    99: ("⛈️", "thunderstorm"),
}


def get_weather_condition(code: int) -> tuple[str, str]:
    """Returns (icon, condition_key) for a given WMO weather code."""
    return WMO_WEATHER_CODES.get(code, ("🌤️", "partly_cloudy"))


def fetch_7day_weather(
    lat: float, lon: float, region_name: str, lang: str = "uz"
) -> Dict[str, Any]:
    """
    Fetches 7-day weather forecast from Open-Meteo API for given coordinates.
    Returns structured days forecast and formatted text message.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max,precipitation_probability_max",
            "timezone": "Asia/Tashkent",
            "forecast_days": 7,
        }

        response = http_get(url, params=params, timeout=HTTP_TIMEOUT)

        if response.status_code != 200:
            # Also try legacy weathercode without underscore if needed
            params["daily"] = "weathercode,temperature_2m_max,temperature_2m_min,windspeed_10m_max,precipitation_probability_max"
            response = http_get(url, params=params, timeout=HTTP_TIMEOUT)

        if response.status_code != 200:
            logger.error("Open-Meteo returned HTTP %s: %s", response.status_code, response.text)
            return {"success": False, "formatted_text": "", "error": "API error"}

        data = response.json()
        daily = data.get("daily", {})

        times = daily.get("time", [])
        weather_codes = daily.get("weather_code") or daily.get("weathercode") or []
        temp_maxs = daily.get("temperature_2m_max", [])
        temp_mins = daily.get("temperature_2m_min", [])
        winds = daily.get("wind_speed_10m_max") or daily.get("windspeed_10m_max") or []
        rains = daily.get("precipitation_probability_max", [])

        if not times:
            return {"success": False, "formatted_text": "", "error": "No daily data"}

        days_count = min(7, len(times))
        header = t("weather_header", lang, region=region_name).strip()
        day_blocks: List[str] = []

        for i in range(days_count):
            date_str = times[i]
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            weekday_name = get_weekday_name(dt.weekday(), lang)
            formatted_date = dt.strftime("%d.%m")

            w_code = weather_codes[i] if i < len(weather_codes) else 0
            icon, desc_key = get_weather_condition(w_code)
            desc_text = get_weather_desc(desc_key, lang)

            max_t = int(round(temp_maxs[i])) if i < len(temp_maxs) else 0
            min_t = int(round(temp_mins[i])) if i < len(temp_mins) else 0
            max_sign = "+" if max_t > 0 else ""
            min_sign = "+" if min_t > 0 else ""

            wind_val = int(round(winds[i])) if i < len(winds) else 0
            rain_val = int(rains[i]) if (i < len(rains) and rains[i] is not None) else 0

            day_block = t(
                "weather_day_format",
                lang,
                day_name=weekday_name,
                date=formatted_date,
                icon=icon,
                desc=desc_text,
                temp_max=f"{max_sign}{max_t}",
                temp_min=f"{min_sign}{min_t}",
                wind=wind_val,
                rain=rain_val,
            ).strip()
            day_blocks.append(day_block)

        formatted_result = f"{header}\n\n" + "\n\n".join(day_blocks)
        return {
            "success": True,
            "formatted_text": formatted_result.strip(),
            "error": None,
        }

    except Exception as e:
        logger.error("Unexpected error in fetch_7day_weather: %s", e)
        return {"success": False, "formatted_text": "", "error": str(e)}
