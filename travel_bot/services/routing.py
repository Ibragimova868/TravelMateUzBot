"""
Routing and distance calculation service for Sayohatchi Bot.
Computes real road distances and travel times using OpenRouteService.
Includes profile mapping for transport modes and resilient fallbacks.
"""

import logging
from typing import Dict, Any, Optional
from config import OPENROUTESERVICE_API_KEY, HTTP_TIMEOUT
from services.http_client import http_get, http_post
from translations import t

logger = logging.getLogger(__name__)

# ============================================================================
# OpenRouteService Profile Mapping
# OpenRouteService v2 officially supports:
# - 'driving-car'
# - 'cycling-regular'
# - 'foot-walking'
# Note: OpenRouteService does NOT provide a distinct 'motorcycle' profile in v2 directions.
# Therefore, 'motorcycle' is mapped to 'driving-car' which shares identical road topology.
# ============================================================================
TRANSPORT_PROFILE_MAPPING = {
    "foot-walking": "foot-walking",
    "cycling-regular": "cycling-regular",
    "driving-car": "driving-car",
    "motorcycle": "driving-car",  # Mapped to 'driving-car' as per ORS API specification
}


def format_duration(seconds: float, lang: str = "uz") -> str:
    """Formats duration in seconds into human-readable hours and minutes."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if lang == "ru":
        if hours > 0 and minutes > 0:
            return f"{hours} ч {minutes} мин"
        elif hours > 0:
            return f"{hours} ч"
        else:
            return f"{max(1, minutes)} мин"
    elif lang == "en":
        if hours > 0 and minutes > 0:
            return f"{hours} hr {minutes} min"
        elif hours > 0:
            return f"{hours} hr"
        else:
            return f"{max(1, minutes)} min"
    else:  # uz (default)
        if hours > 0 and minutes > 0:
            return f"{hours} soat {minutes} daqiqa"
        elif hours > 0:
            return f"{hours} soat"
        else:
            return f"{max(1, minutes)} daqiqa"


def format_distance(meters: float, lang: str = "uz") -> str:
    """Formats distance in meters into kilometers or meters."""
    if meters >= 1000:
        km = meters / 1000.0
        if km >= 10:
            km_formatted = f"{int(round(km))}"
        else:
            km_formatted = f"{km:.1f}"

        if lang == "ru":
            return f"{km_formatted} км"
        elif lang == "en":
            return f"{km_formatted} km"
        else:
            return f"{km_formatted} km"
    else:
        m = int(round(meters))
        if lang == "ru":
            return f"{m} м"
        elif lang == "en":
            return f"{m} m"
        else:
            return f"{m} m"


def calculate_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    transport_key: str = "driving-car",
    lang: str = "uz",
) -> Dict[str, Any]:
    """
    Calculates road distance and travel duration between two coordinates.
    Returns:
    {
        "success": bool,
        "distance_meters": float,
        "duration_seconds": float,
        "formatted_distance": str,
        "formatted_duration": str,
        "profile_used": str,
        "error": Optional[str]
    }
    """
    # Map requested transport key to supported ORS profile
    ors_profile = TRANSPORT_PROFILE_MAPPING.get(transport_key, "driving-car")

    # 1. Primary engine: OpenRouteService API
    if OPENROUTESERVICE_API_KEY:
        try:
            url = f"https://api.openrouteservice.org/v2/directions/{ors_profile}"
            headers = {
                "Authorization": OPENROUTESERVICE_API_KEY,
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json, application/geo+json",
            }
            payload = {
                "coordinates": [
                    [start_lon, start_lat],
                    [end_lon, end_lat],
                ]
            }

            response = http_post(
                url, json_data=payload, headers=headers, timeout=HTTP_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                routes = data.get("routes", [])
                if routes:
                    summary = routes[0].get("summary", {})
                    distance_m = float(summary.get("distance", 0.0))
                    duration_s = float(summary.get("duration", 0.0))

                    return {
                        "success": True,
                        "distance_meters": distance_m,
                        "duration_seconds": duration_s,
                        "formatted_distance": format_distance(distance_m, lang),
                        "formatted_duration": format_duration(duration_s, lang),
                        "profile_used": ors_profile,
                        "error": None,
                    }
            else:
                logger.warning(
                    "ORS Directions HTTP %s: %s",
                    response.status_code,
                    response.text[:200],
                )
        except Exception as e:
            logger.warning("ORS directions request failed: %s. Trying fallback...", e)

    # 2. Resilient OpenStreetMap OSRM fallback (ensures bot works even if ORS key is not yet set)
    try:
        osrm_mode = "car"
        if ors_profile == "foot-walking":
            osrm_mode = "foot"
        elif ors_profile == "cycling-regular":
            osrm_mode = "bicycle"

        osrm_url = (
            f"http://router.project-osrm.org/route/v1/{osrm_mode}/"
            f"{start_lon},{start_lat};{end_lon},{end_lat}?overview=false"
        )
        headers = {"User-Agent": "SayohatchiTelegramBot/2.0"}
        response = http_get(osrm_url, headers=headers, timeout=HTTP_TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "Ok" and data.get("routes"):
                route = data["routes"][0]
                distance_m = float(route.get("distance", 0.0))
                duration_s = float(route.get("duration", 0.0))

                return {
                    "success": True,
                    "distance_meters": distance_m,
                    "duration_seconds": duration_s,
                    "formatted_distance": format_distance(distance_m, lang),
                    "formatted_duration": format_duration(duration_s, lang),
                    "profile_used": f"osrm-{osrm_mode}",
                    "error": None,
                }
    except Exception as e:
        logger.error("OSRM fallback routing failed: %s", e)

    return {
        "success": False,
        "distance_meters": 0.0,
        "duration_seconds": 0.0,
        "formatted_distance": "",
        "formatted_duration": "",
        "profile_used": ors_profile,
        "error": t("route_calc_error", lang),
    }
