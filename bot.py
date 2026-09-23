#!/usr/bin/env python3
"""
Sayohatchi Telegram Bot - Main Application Entrypoint
A complete travel, navigation, 7-day weather, and nearby-places assistant for Uzbekistan.

Supports:
- 🇺🇿 O‘zbek (default)
- 🇷🇺 Русский
- 🇬🇧 English
"""

import sys
import logging
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database import init_db
from handlers import (
    get_registration_handler,
    get_routing_handler,
    register_weather_handlers,
    register_nearby_handlers,
    get_profile_handler,
    register_language_handlers,
    register_menu_handlers,
    global_error_handler,
    unknown_message_handler,
)

# Configure logging format and level
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("SayohatchiBot")


def main() -> None:
    """Initializes the database and runs the Telegram bot."""
    logger.info("Initializing database...")
    init_db()

    if not BOT_TOKEN:
        logger.error(
            "ERROR: BOT_TOKEN is not set!\n"
            "Please create a .env file based on .env.example and provide your Telegram Bot Token from @BotFather.\n"
            "Example: BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ"
        )
        sys.exit(1)

    logger.info("Building Telegram Application...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 1. Registration & Onboarding ConversationHandler
    app.add_handler(get_registration_handler())

    # 2. Distance and Routing ConversationHandler
    app.add_handler(get_routing_handler())

    # 3. Profile Edit ConversationHandler
    app.add_handler(get_profile_handler())

    # 4. 7-Day Weather Handlers
    register_weather_handlers(app)

    # 5. Nearby Places Handlers
    register_nearby_handlers(app)

    # 6. Language Selection Handlers
    register_language_handlers(app)

    # 7. Menu, Navigation & About Handlers
    register_menu_handlers(app)

    # 8. Catch-all for unhandled text messages
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message_handler)
    )

    # 9. Global Error Handler
    app.add_error_handler(global_error_handler)

    logger.info("Sayohatchi Bot is starting polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
