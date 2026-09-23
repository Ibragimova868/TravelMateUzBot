"""
Handlers package exports.
"""

from handlers.start import get_registration_handler
from handlers.routing import get_routing_handler
from handlers.weather import register_weather_handlers
from handlers.nearby import register_nearby_handlers
from handlers.profile import get_profile_handler, show_profile
from handlers.language import register_language_handlers
from handlers.menu import register_menu_handlers, global_error_handler, unknown_message_handler

__all__ = [
    "get_registration_handler",
    "get_routing_handler",
    "register_weather_handlers",
    "register_nearby_handlers",
    "get_profile_handler",
    "show_profile",
    "register_language_handlers",
    "register_menu_handlers",
    "global_error_handler",
    "unknown_message_handler",
]
