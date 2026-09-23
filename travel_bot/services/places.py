"""
Nearby places service for Sayohatchi Bot.
Designed with a provider interface allowing seamless switching between OpenStreetMap Overpass
and Google Places API without rewriting handlers.
"""

import math
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from config import HTTP_TIMEOUT, GOOGLE_PLACES_API_KEY
from services.http_client import http_get, http_post
from services.routing import format_distance

logger = logging.getLogger(__name__)


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculates great-circle distance between two points in meters using Haversine formula.
    """
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class PlaceItem:
    """Data transfer object for a nearby place."""

    def __init__(
        self,
        name: str,
        address: str,
        distance_meters: float,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ):
        self.name = name
        self.address = address
        self.distance_meters = distance_meters
        self.lat = lat
        self.lon = lon

    def to_dict(self, lang: str = "uz") -> Dict[str, Any]:
        return {
            "name": self.name,
            "address": self.address,
            "distance_meters": self.distance_meters,
            "formatted_distance": format_distance(self.distance_meters, lang),
            "lat": self.lat,
            "lon": self.lon,
        }


class PlacesProvider(ABC):
    """Abstract interface for nearby places search providers."""

    @abstractmethod
    def search_nearby(
        self, lat: float, lon: float, category: str, radius_meters: int = 3500
    ) -> List[PlaceItem]:
        pass


class OverpassPlacesProvider(PlacesProvider):
    """
    Free and open provider using OpenStreetMap Overpass API.
    Supports primary travel categories: pharmacy, cafe, hotel, fuel, bank, shop.
    """

    OVERPASS_ENDPOINTS = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
    ]

    TAG_FILTERS = {
        "pharmacy": '["amenity"="pharmacy"]',
        "cafe": '["amenity"~"cafe|restaurant|fast_food"]',
        "hotel": '["tourism"~"hotel|hostel|guest_house|motel"]',
        "fuel": '["amenity"="fuel"]',
        "bank": '["amenity"~"bank|atm"]',
        "shop": '["shop"~"supermarket|convenience|grocery|department_store"]',
    }

    DEFAULT_NAMES = {
        "pharmacy": "Dorixona / Аптека",
        "cafe": "Kafe / Кафе",
        "hotel": "Mehmonxona / Отель",
        "fuel": "Yoqilg‘i shoxobchasi / АЗС",
        "bank": "Bank / Банкомат",
        "shop": "Do‘kon / Магазин",
    }

    def search_nearby(
        self, lat: float, lon: float, category: str, radius_meters: int = 3500
    ) -> List[PlaceItem]:
        tag_filter = self.TAG_FILTERS.get(category, '["amenity"="pharmacy"]')
        default_name = self.DEFAULT_NAMES.get(category, "Noma'lum joy")

        query = f"""
        [out:json][timeout:10];
        (
          node{tag_filter}(around:{radius_meters},{lat},{lon});
          way{tag_filter}(around:{radius_meters},{lat},{lon});
        );
        out center 15;
        """

        results: List[PlaceItem] = []

        for endpoint in self.OVERPASS_ENDPOINTS:
            try:
                response = http_post(
                    endpoint,
                    data={"data": query},
                    headers={"User-Agent": "SayohatchiTelegramBot/2.0"},
                    timeout=HTTP_TIMEOUT,
                )

                if response.status_code == 200:
                    data = response.json()
                    elements = data.get("elements", [])

                    for el in elements:
                        p_lat = el.get("lat") or el.get("center", {}).get("lat")
                        p_lon = el.get("lon") or el.get("center", {}).get("lon")
                        if p_lat is None or p_lon is None:
                            continue

                        dist = calculate_haversine_distance(lat, lon, float(p_lat), float(p_lon))
                        tags = el.get("tags", {})
                        name = (
                            tags.get("name")
                            or tags.get("name:uz")
                            or tags.get("name:ru")
                            or tags.get("name:en")
                            or tags.get("brand")
                            or tags.get("operator")
                            or default_name
                        )

                        addr_parts = []
                        if tags.get("addr:street"):
                            street = tags.get("addr:street")
                            if tags.get("addr:housenumber"):
                                street += f", {tags.get('addr:housenumber')}"
                            addr_parts.append(street)
                        if tags.get("addr:district"):
                            addr_parts.append(tags.get("addr:district"))
                        if tags.get("addr:city"):
                            addr_parts.append(tags.get("addr:city"))

                        address = (
                            ", ".join(addr_parts)
                            if addr_parts
                            else f"Koordinata: {float(p_lat):.4f}, {float(p_lon):.4f}"
                        )

                        results.append(
                            PlaceItem(
                                name=name,
                                address=address,
                                distance_meters=dist,
                                lat=float(p_lat),
                                lon=float(p_lon),
                            )
                        )

                    break
            except Exception as e:
                logger.warning("Overpass error on %s: %s", endpoint, e)

        # Sort places strictly by closest distance
        results.sort(key=lambda p: p.distance_meters)
        return results[:8]


class GooglePlacesProvider(PlacesProvider):
    """
    Google Places API provider implementation.
    Can be used by configuring GOOGLE_PLACES_API_KEY in .env.
    """

    GOOGLE_TYPE_MAPPING = {
        "pharmacy": "pharmacy",
        "cafe": "cafe",
        "hotel": "lodging",
        "fuel": "gas_station",
        "bank": "bank",
        "shop": "supermarket",
    }

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_nearby(
        self, lat: float, lon: float, category: str, radius_meters: int = 3500
    ) -> List[PlaceItem]:
        if not self.api_key:
            return []

        place_type = self.GOOGLE_TYPE_MAPPING.get(category, "pharmacy")
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lon}",
            "radius": radius_meters,
            "type": place_type,
            "key": self.api_key,
        }

        try:
            response = http_get(url, params=params, timeout=HTTP_TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("results", []):
                    geometry = item.get("geometry", {}).get("location", {})
                    p_lat = geometry.get("lat")
                    p_lon = geometry.get("lng")
                    dist = (
                        calculate_haversine_distance(lat, lon, float(p_lat), float(p_lon))
                        if (p_lat and p_lon)
                        else 0.0
                    )
                    results.append(
                        PlaceItem(
                            name=item.get("name", "Unknown Place"),
                            address=item.get("vicinity", "Near current location"),
                            distance_meters=dist,
                            lat=float(p_lat) if p_lat else None,
                            lon=float(p_lon) if p_lon else None,
                        )
                    )
                results.sort(key=lambda p: p.distance_meters)
                return results[:8]
        except Exception as e:
            logger.error("Google Places request error: %s", e)

        return []


class PlacesService:
    """
    Facade service orchestrating nearby places search.
    Defaults to Overpass provider, seamlessly switches to Google Places if configured.
    """

    def __init__(self):
        if GOOGLE_PLACES_API_KEY:
            self.provider: PlacesProvider = GooglePlacesProvider(GOOGLE_PLACES_API_KEY)
            logger.info("Using GooglePlacesProvider for nearby places.")
        else:
            self.provider = OverpassPlacesProvider()
            logger.info("Using OverpassPlacesProvider for nearby places.")

    def find_nearby(
        self, lat: float, lon: float, category: str, lang: str = "uz"
    ) -> Dict[str, Any]:
        """
        Executes nearby search and returns formatted result text or empty indicator.
        """
        try:
            places = self.provider.search_nearby(lat, lon, category)
            if not places:
                return {
                    "success": True,
                    "count": 0,
                    "places": [],
                    "formatted_items": [],
                    "error": None,
                }

            formatted_items = []
            for idx, p in enumerate(places, start=1):
                item_dict = p.to_dict(lang)
                item_dict["index"] = idx
                formatted_items.append(item_dict)

            return {
                "success": True,
                "count": len(formatted_items),
                "places": formatted_items,
                "error": None,
            }
        except Exception as e:
            logger.error("find_nearby error: %s", e)
            return {
                "success": False,
                "count": 0,
                "places": [],
                "formatted_items": [],
                "error": str(e),
            }


# Singleton service instance for handlers
places_service = PlacesService()
