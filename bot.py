import logging
import sys
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import BOT_TOKEN
from database import init_db
from handlers.common import (
    start_command,
    help_command,
    profile_command,
    language_command,
    handle_callback,
    handle_text_messages
)
from handlers.route import (
    route_command,
    handle_route_location,
    handle_route_destination_input
)
from handlers.places import (
    nearby_command,
    handle_nearby_location
)
from handlers.itinerary import (
    weather_command,
    handle_weather_city_selection,
    plan_command
)
from handlers.packing import pack_command

# Logging sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Telegram Bot is running smoothly and 100% FREE!")

    def log_message(self, format, *args):
        return

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health-check server {port}-portda ishga tushdi...")
    server.serve_forever()

def main():
    """Botni ishga tushirish funksiyasi."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN aniqlanmadi! Iltimos, .env faylida BOT_TOKEN ni belgilang.")
        sys.exit(1)

    init_db()

    # Bepul Render Web Service uchun fon rejimida mini-server
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("route", route_command))
    app.add_handler(CommandHandler("nearby", nearby_command))
    app.add_handler(CommandHandler("weather", weather_command))
    app.add_handler(CommandHandler("plan", plan_command))
    app.add_handler(CommandHandler("pack", pack_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("lang", language_command))

    app.add_handler(CallbackQueryHandler(handle_weather_city_selection, pattern="^weather_"))
    app.add_handler(CallbackQueryHandler(handle_callback))

    app.add_handler(MessageHandler(filters.LOCATION, handle_route_location))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_route_destination_input
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_messages
    ))

    logger.info("Bot muvaffaqiyatli ishga tushdi...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
