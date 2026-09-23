"""
Language switching handler for Sayohatchi Bot.
Updates user language preference in SQLite and refreshes UI.
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
from database import update_user_language, get_user_language
from translations import t
from keyboards import get_language_keyboard, get_main_menu_keyboard

logger = logging.getLogger(__name__)


async def language_menu_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Shows the language selection inline keyboard."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    text = t("choose_new_language", lang)
    reply_markup = get_language_keyboard(is_change=True, lang=lang)

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def change_language_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Updates user language in SQLite and sends refreshed main menu."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    if not user:
        return

    data = query.data
    new_lang = "uz"
    if data == "set_lang_ru":
        new_lang = "ru"
    elif data == "set_lang_en":
        new_lang = "en"

    # Persist language preference to SQLite
    update_user_language(user.id, new_lang)

    confirm_msg = t("language_updated", new_lang)
    await query.edit_message_text(confirm_msg)

    # Send persistent main menu keyboard in the newly chosen language
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=t("menu_title", new_lang),
            reply_markup=get_main_menu_keyboard(new_lang),
        )


def register_language_handlers(app) -> None:
    """Registers language handlers with Telegram application."""
    app.add_handler(
        MessageHandler(
            filters.Regex(
                r"^(🌐 Tilni o‘zgartirish|🌐 Изменить язык|🌐 Change Language)$"
            ),
            language_menu_command,
        )
    )
    app.add_handler(CommandHandler("language", language_menu_command))
    app.add_handler(
        CallbackQueryHandler(language_menu_command, pattern="^prof_change_lang$")
    )
    app.add_handler(
        CallbackQueryHandler(change_language_callback, pattern="^set_lang_")
    )
