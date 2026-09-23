"""
Menu, Navigation, and General handlers for Sayohatchi Bot.
Includes About section, Back-to-menu routing, and Global Error Handler.
"""

import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from database import get_user_language
from translations import t
from keyboards import get_main_menu_keyboard
from handlers.profile import show_profile

logger = logging.getLogger(__name__)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays information about the bot and its features."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    about_text = t("about_text", lang)
    if update.message:
        await update.message.reply_text(
            about_text, reply_markup=get_main_menu_keyboard(lang)
        )
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            about_text, reply_markup=get_main_menu_keyboard(lang)
        )


async def back_to_main_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Returns user to the primary main menu."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    menu_text = t("menu_title", lang)
    if update.message:
        await update.message.reply_text(
            menu_text, reply_markup=get_main_menu_keyboard(lang)
        )
    elif update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=menu_text,
                reply_markup=get_main_menu_keyboard(lang),
            )


async def unknown_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Gracefully handles arbitrary or unmapped text messages."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    if update.message:
        await update.message.reply_text(
            t("unknown_command", lang),
            reply_markup=get_main_menu_keyboard(lang),
        )


async def global_error_handler(
    update: object, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Global error handler for the bot application.
    Logs error internally without leaking tokens or stack traces to the user.
    """
    logger.error("Exception occurred while handling update: %s", context.error, exc_info=context.error)

    if isinstance(update, Update) and update.effective_user:
        try:
            lang = get_user_language(update.effective_user.id)
            err_msg = t("service_error", lang)
            if update.effective_message:
                await update.effective_message.reply_text(
                    err_msg, reply_markup=get_main_menu_keyboard(lang)
                )
        except Exception as e:
            logger.error("Failed to deliver friendly error to user: %s", e)


def register_menu_handlers(app) -> None:
    """Registers general menu and navigation handlers."""
    # About bot
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^(ℹ️ Bot haqida|ℹ️ О боте|ℹ️ About Bot)$"),
            about_command,
        )
    )
    app.add_handler(CommandHandler("about", about_command))

    # Profile
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^(👤 Profilim|👤 Мой профиль|👤 My Profile)$"),
            show_profile,
        )
    )
    app.add_handler(CommandHandler("profile", show_profile))

    # Back button handlers
    app.add_handler(
        MessageHandler(
            filters.Regex(r"^(🔙 Orqaga|🔙 Назад|🔙 Back)$"),
            back_to_main_menu,
        )
    )
    app.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^back_to_menu$"))
