"""
Comprehensive automated unit and flow tests for Sayohatchi Bot.
Simulates original tests 1-10 and new coordinate routing tests (TEST 1 - TEST 9).
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import database
from translations import t, get_language_display_name, get_weekday_name
from config import UZBEKISTAN_REGIONS
from services.geocoding import (
    geocode_address,
    parse_coordinates,
    validate_coordinates,
    resolve_location_input,
)
from services.routing import calculate_route, format_distance, format_duration
from services.weather import fetch_7day_weather, get_weather_condition
from services.places import calculate_haversine_distance, PlaceItem, PlacesService


class SayohatchiBotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use an isolated temporary database for testing
        cls.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        database.DATABASE_PATH = cls.temp_db.name
        database.init_db()

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.temp_db.name)
        except Exception:
            pass

    # =========================================================================
    # =========================================================================
    # SECTION 9: REQUIRED TESTS 1 - 10
    # =========================================================================

    def test_01_new_user_registration_flow(self):
        """
        TEST 1:
        New user -> /start -> Welcome message -> Select Uzbek -> First Name -> Last Name -> Main Menu
        """
        tg_id = 111222333
        # Ensure user does not exist
        self.assertIsNone(database.get_user(tg_id))

        # Welcome message in Uzbek
        welcome = t("welcome_new_user", "uz")
        self.assertEqual(welcome, "Assalomu alaykum. Xush kelibsiz!")

        # Language selection prompt
        prompt = t("choose_language_prompt", "uz")
        self.assertIn("tilni tanlang", prompt)

        # First Name prompt
        ask_fn = t("ask_first_name", "uz")
        self.assertEqual(ask_fn, "Ismingizni kiriting:")

        # Last Name prompt
        ask_ln = t("ask_last_name", "uz")
        self.assertEqual(ask_ln, "Familiyangizni kiriting:")

        # Save to SQLite
        ok = database.create_user(
            telegram_id=tg_id,
            first_name="Mohinur",
            last_name="Ibragimova",
            language="uz",
        )
        self.assertTrue(ok)

        # Open Main menu in Uzbek
        user = database.get_user(tg_id)
        self.assertIsNotNone(user)
        self.assertEqual(user["first_name"], "Mohinur")
        self.assertEqual(user["last_name"], "Ibragimova")
        self.assertEqual(user["language"], "uz")
        self.assertIn("📍 Masofa va yo‘l vaqti", t("btn_distance_route", "uz"))

    def test_02_existing_user_start(self):
        """
        TEST 2:
        Existing user -> /start -> Main Menu directly
        """
        tg_id = 111222333
        existing = database.get_user(tg_id)
        self.assertIsNotNone(existing)

        # Does not ask for registration again, returns main menu directly
        welcome_back = t("welcome_back", existing["language"], name=existing["first_name"])
        self.assertIn("Mohinur", welcome_back)
        self.assertIn("Qaytganingiz bilan", welcome_back)

    def test_03_routing_with_coordinates(self):
        """
        TEST 3:
        Routing with coordinates:
        39.7747, 64.4286 -> 41.2995, 69.2401 -> Car -> Route result
        """
        loc1 = resolve_location_input("39.7747, 64.4286")
        loc2 = resolve_location_input("41.2995, 69.2401")

        self.assertTrue(loc1["success"])
        self.assertTrue(loc1["is_coordinate"])
        self.assertTrue(loc2["success"])
        self.assertTrue(loc2["is_coordinate"])

        route = calculate_route(
            start_lat=loc1["lat"],
            start_lon=loc1["lon"],
            end_lat=loc2["lat"],
            end_lon=loc2["lon"],
            transport_key="driving-car",
            lang="uz",
        )
        self.assertTrue(route["success"])
        self.assertGreater(route["distance_meters"], 400000)
        self.assertIn("km", route["formatted_distance"])
        self.assertIn("soat", route["formatted_duration"])

    def test_04_routing_with_normal_address(self):
        """
        TEST 4:
        Routing with normal address:
        Bukhara -> Tashkent -> Car -> Route result
        """
        loc1 = resolve_location_input("Bukhara")
        loc2 = resolve_location_input("Tashkent")

        self.assertTrue(loc1["success"])
        self.assertFalse(loc1["is_coordinate"])
        self.assertTrue(loc2["success"])
        self.assertFalse(loc2["is_coordinate"])

        route = calculate_route(
            start_lat=loc1["lat"],
            start_lon=loc1["lon"],
            end_lat=loc2["lat"],
            end_lon=loc2["lon"],
            transport_key="driving-car",
            lang="uz",
        )
        self.assertTrue(route["success"])
        self.assertGreater(route["distance_meters"], 400000)

    def test_05_mixed_routing(self):
        """
        TEST 5:
        Mixed routing:
        39.7747, 64.4286 -> Tashkent -> Car -> Route result
        """
        loc1 = resolve_location_input("39.7747, 64.4286")
        loc2 = resolve_location_input("Tashkent")

        self.assertTrue(loc1["success"])
        self.assertTrue(loc1["is_coordinate"])
        self.assertTrue(loc2["success"])
        self.assertFalse(loc2["is_coordinate"])

        route = calculate_route(
            start_lat=loc1["lat"],
            start_lon=loc1["lon"],
            end_lat=loc2["lat"],
            end_lon=loc2["lon"],
            transport_key="driving-car",
            lang="uz",
        )
        self.assertTrue(route["success"])
        self.assertGreater(route["distance_meters"], 400000)

    def test_06_weather_buxoro_7day(self):
        """
        TEST 6:
        Weather:
        Weather -> Buxoro -> 7-day forecast -> Exactly 7 days -> Correct weekdays -> Actual API values
        """
        buxoro = UZBEKISTAN_REGIONS["buxoro"]
        self.assertEqual(len(UZBEKISTAN_REGIONS), 12)

        res = fetch_7day_weather(
            lat=buxoro["lat"],
            lon=buxoro["lon"],
            region_name=buxoro["name_uz"],
            lang="uz",
        )
        self.assertTrue(res["success"])
        text = res["formatted_text"]
        self.assertIn("Buxoro — 7 kunlik ob-havo", text)
        self.assertIn("°C", text)
        self.assertIn("Shamol:", text)
        self.assertIn("Yog‘ingarchilik ehtimoli:", text)

        # Verify exactly 7 calendar day blocks are present
        day_occurrences = text.count("📅")
        self.assertEqual(day_occurrences, 7)

    def test_07_weather_tashkent_7day(self):
        """
        TEST 7:
        Weather:
        Weather -> Tashkent -> 7-day forecast -> Correct Tashkent weather data
        """
        toshkent = UZBEKISTAN_REGIONS["toshkent"]
        res = fetch_7day_weather(
            lat=toshkent["lat"],
            lon=toshkent["lon"],
            region_name=toshkent["name_uz"],
            lang="uz",
        )
        self.assertTrue(res["success"])
        text = res["formatted_text"]
        self.assertIn("Toshkent — 7 kunlik ob-havo", text)
        self.assertEqual(text.count("📅"), 7)

    def test_08_profile_display_and_fields(self):
        """
        TEST 8:
        Profile:
        Profile -> First Name -> Last Name -> Language -> Registration date
        """
        tg_id = 111222333
        user = database.get_user(tg_id)
        self.assertIsNotNone(user)

        # Date formatting DD.MM.YYYY
        created_at_raw = str(user["created_at"]).split()[0]
        parts = created_at_raw.split("-")
        formatted_date = f"{parts[2]}.{parts[1]}.{parts[0]}" if len(parts) == 3 else created_at_raw

        card = t(
            "profile_title",
            user["language"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            language=get_language_display_name(user["language"]),
            created_at=formatted_date,
        )
        self.assertIn("👤 Profilim", card)
        self.assertIn("Ism: Mohinur", card)
        self.assertIn("Familiya: Ibragimova", card)
        self.assertIn("🌐 Til: O‘zbek", card)
        self.assertIn("📅 Ro‘yxatdan o‘tgan sana:", card)

    def test_09_invalid_coordinates(self):
        """
        TEST 9:
        Invalid coordinates:
        100.1234, 64.4286 -> Friendly localized error
        """
        loc = resolve_location_input("100.1234, 64.4286")
        self.assertFalse(loc["success"])
        self.assertEqual(loc["error_key"], "invalid_coordinates")

        err_uz = t(loc["error_key"], "uz")
        err_ru = t(loc["error_key"], "ru")
        err_en = t(loc["error_key"], "en")
        self.assertIn("39.7747, 64.4286", err_uz)
        self.assertIn("39.7747, 64.4286", err_ru)
        self.assertIn("39.7747, 64.4286", err_en)

    def test_10_api_failure_handling(self):
        """
        TEST 10:
        API failure -> Friendly localized error -> Bot continues working
        """
        route_err = calculate_route(
            start_lat=0.0,
            start_lon=0.0,
            end_lat=0.0,
            end_lon=0.0,
            transport_key="driving-car",
            lang="uz",
        )
        self.assertIsInstance(route_err, dict)
        self.assertFalse(route_err["success"])
        self.assertIn("hisoblab bo‘lmadi", route_err["error"].lower())

    # =========================================================================
    # COORDINATE INPUT FEATURE TESTS (USER REQUEST TESTS 1-9)
    # =========================================================================

    def test_coord_01_coordinate_to_coordinate_routing(self):
        """USER TEST 1: 39.7747, 64.4286 -> 41.2995, 69.2401 -> Car -> Route successfully."""
        loc1 = resolve_location_input("39.7747, 64.4286")
        loc2 = resolve_location_input("41.2995, 69.2401")

        self.assertTrue(loc1["success"])
        self.assertTrue(loc1["is_coordinate"])
        self.assertAlmostEqual(loc1["lat"], 39.7747, places=4)
        self.assertAlmostEqual(loc1["lon"], 64.4286, places=4)

        self.assertTrue(loc2["success"])
        self.assertTrue(loc2["is_coordinate"])
        self.assertAlmostEqual(loc2["lat"], 41.2995, places=4)
        self.assertAlmostEqual(loc2["lon"], 69.2401, places=4)

        route = calculate_route(
            start_lat=loc1["lat"],
            start_lon=loc1["lon"],
            end_lat=loc2["lat"],
            end_lon=loc2["lon"],
            transport_key="driving-car",
            lang="uz",
        )
        self.assertTrue(route["success"])
        self.assertGreater(route["distance_meters"], 400000)

    def test_coord_02_address_to_coordinate_mixed(self):
        """USER TEST 2: Bukhara -> 41.2995, 69.2401 -> Car -> Route successfully."""
        loc1 = resolve_location_input("Bukhara")
        loc2 = resolve_location_input("41.2995, 69.2401")

        self.assertTrue(loc1["success"])
        self.assertFalse(loc1["is_coordinate"])
        self.assertIsNotNone(loc1["lat"])

        self.assertTrue(loc2["success"])
        self.assertTrue(loc2["is_coordinate"])

        route = calculate_route(
            start_lat=loc1["lat"],
            start_lon=loc1["lon"],
            end_lat=loc2["lat"],
            end_lon=loc2["lon"],
            transport_key="driving-car",
            lang="uz",
        )
        self.assertTrue(route["success"])

    def test_coord_03_coordinate_to_address_mixed(self):
        """USER TEST 3: 39.7747, 64.4286 -> Tashkent -> Car -> Route successfully."""
        loc1 = resolve_location_input("39.7747, 64.4286")
        loc2 = resolve_location_input("Tashkent")

        self.assertTrue(loc1["success"])
        self.assertTrue(loc1["is_coordinate"])
        self.assertTrue(loc2["success"])
        self.assertFalse(loc2["is_coordinate"])

        route = calculate_route(
            start_lat=loc1["lat"],
            start_lon=loc1["lon"],
            end_lat=loc2["lat"],
            end_lon=loc2["lon"],
            transport_key="driving-car",
            lang="uz",
        )
        self.assertTrue(route["success"])

    def test_coord_04_latitude_out_of_range(self):
        """USER TEST 4: 100.1234, 64.4286 -> Friendly invalid-coordinate message."""
        loc = resolve_location_input("100.1234, 64.4286")
        self.assertFalse(loc["success"])
        self.assertEqual(loc["error_key"], "invalid_coordinates")

        # Verify localized messages in all 3 languages
        msg_uz = t("invalid_coordinates", "uz")
        msg_ru = t("invalid_coordinates", "ru")
        msg_en = t("invalid_coordinates", "en")
        self.assertIn("39.7747, 64.4286", msg_uz)
        self.assertIn("39.7747, 64.4286", msg_ru)
        self.assertIn("39.7747, 64.4286", msg_en)

    def test_coord_05_single_number_coordinate(self):
        """USER TEST 5: 39.7747 -> Friendly invalid-coordinate message / input-validation response."""
        loc = resolve_location_input("39.7747")
        self.assertFalse(loc["success"])
        self.assertEqual(loc["error_key"], "invalid_coordinates")

    def test_coord_06_no_spaces_format(self):
        """USER TEST 6: 39.7747,64.4286 -> Works successfully."""
        coords = parse_coordinates("39.7747,64.4286")
        self.assertIsNotNone(coords)
        lat, lon = coords
        self.assertAlmostEqual(lat, 39.7747, places=4)
        self.assertAlmostEqual(lon, 64.4286, places=4)

        loc = resolve_location_input("39.7747,64.4286")
        self.assertTrue(loc["success"])
        self.assertTrue(loc["is_coordinate"])

    def test_coord_07_spaces_around_comma(self):
        """USER TEST 7: 39.7747 , 64.4286 -> Works successfully."""
        coords = parse_coordinates("39.7747 , 64.4286")
        self.assertIsNotNone(coords)
        lat, lon = coords
        self.assertAlmostEqual(lat, 39.7747, places=4)
        self.assertAlmostEqual(lon, 64.4286, places=4)

        loc = resolve_location_input("39.7747 , 64.4286")
        self.assertTrue(loc["success"])
        self.assertTrue(loc["is_coordinate"])

    def test_coord_08_non_numeric_comma(self):
        """USER TEST 8: abc, xyz -> Handle safely without crashing."""
        coords = parse_coordinates("abc, xyz")
        self.assertIsNone(coords)

        # resolve_location_input should safely handle input without crashing
        loc = resolve_location_input("abc, xyz")
        self.assertIsInstance(loc, dict)
        self.assertIn("success", loc)
        self.assertIn("is_coordinate", loc)
        self.assertFalse(loc["is_coordinate"])  # Must not be identified as raw coordinates

    def test_coord_09_empty_input(self):
        """USER TEST 9: Empty input -> Handle safely without crashing."""
        coords = parse_coordinates("")
        self.assertIsNone(coords)

        loc = resolve_location_input("")
        self.assertIsInstance(loc, dict)
        self.assertFalse(loc["success"])
        self.assertIn(loc["error_key"], ["invalid_input", "route_address_not_found"])


if __name__ == "__main__":
    unittest.main()
