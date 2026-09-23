"""
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
    """
    Validates that latitude is within [-90, 90] and longitude is within [-180, 180].
    """
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0


def parse_coordinates(text: str) -> Optional[Tuple[float, float]]:
    """
    Parses a string containing latitude and longitude separated by a comma.
    Whitespace around values is ignored.
    Returns (lat, lon) tuple if valid, or None if the text is not valid coordinates.

    Examples of valid coordinates:
    - "39.7747, 64.4286"
    - "39.7747,64.4286"
    - "39.7747 , 64.4286"
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
    1. Direct valid coordinates (e.g. '39.7747, 64.4286')
       -> Returns immediately with coordinates; NO geocoding API is invoked.
    2. Malformed or out-of-range coordinate attempt (e.g. '100.1234, 64.4286', '39.7747', '39.7747, 200')
       -> Returns success=False, error_key="invalid_coordinates".
    3. Text address (e.g. 'Bukhara', 'Tashkent, Amir Temur Street')
       -> Geocodes address via OpenRouteService or Nominatim.

    Returns:
    {
        "success": bool,
        "lat": Optional[float],
        "lon": Optional[float],
        "display_name": str,
        "is_coordinate": bool,
        "error_key": Optional[str],
        "error": Optional[str]
    }
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
        # Format cleanly, preserving up to 4-6 decimal places as input
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
    # Case A: Standalone float without longitude (e.g. "39.7747")
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

    # Case B: Comma-separated with numbers that are out-of-bounds
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
                # Not pure numbers (e.g. "Tashkent, Amir Temur" or "abc, xyz")
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
    """
    Geocodes an address or city name into (latitude, longitude, display_name).
    Returns a dictionary with status, coordinates, and cleaned display name.
    """
    clean_query = query.strip()
    if not clean_query:
        return {
            "success": False,
            "lat": None,
            "lon": None,
            "display_name": "",
            "error": "Empty query",
        }

    # 1. Try OpenRouteService Geocoding API if key is present
    if OPENROUTESERVICE_API_KEY:
        try:
            url = "https://api.openrouteservice.org/geocode/search"
            params = {
                "api_key": OPENROUTESERVICE_API_KEY,
                "text": clean_query,
                "size": 1,
            }
            response = http_get(url, params=params, timeout=HTTP_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                if features:
                    feat = features[0]
                    coords = feat.get("geometry", {}).get("coordinates", [])
                    props = feat.get("properties", {})
                    if len(coords) >= 2:
                        lon, lat = float(coords[0]), float(coords[1])
                        label = props.get("label", clean_query)
                        return {
                            "success": True,
                            "lat": lat,
                            "lon": lon,
                            "display_name": label,
                            "error": None,
                        }
            else:
                logger.warning(
                    "ORS geocoding returned status %s: %s",
                    response.status_code,
                    response.text[:200],
                )
        except Exception as e:
            logger.warning("ORS Geocoding request error: %s. Trying fallback...", e)

    # 2. Resilient fallback: OpenStreetMap Nominatim
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": clean_query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }
        headers = {"User-Agent": "SayohatchiTelegramBot/2.0 (Uzbekistan Travel Assistant)"}
        response = http_get(url, params=params, headers=headers, timeout=HTTP_TIMEOUT)

        if response.status_code == 200:
            results = response.json()
            if results and len(results) > 0:
                first = results[0]
                lat = float(first["lat"])
                lon = float(first["lon"])
                display_name = first.get("display_name", clean_query)
                # Shorten long address for nice UI presentation
                parts = [p.strip() for p in display_name.split(",") if p.strip()]
                short_name = ", ".join(parts[:3]) if len(parts) > 3 else display_name

                return {
                    "success": True,
                    "lat": lat,
                    "lon": lon,
                    "display_name": short_name,
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "lat": None,
                    "lon": None,
                    "display_name": "",
                    "error": "Address not found",
                }
        else:
            return {
                "success": False,
                "lat": None,
                "lon": None,
                "display_name": "",
                "error": f"Geocoding HTTP error {response.status_code}",
            }
    except Exception as e:
        logger.error("Nominatim fallback request error: %s", e)
        return {
            "success": False,
            "lat": None,
            "lon": None,
            "display_name": "",
            "error": "Connection error",
        }
