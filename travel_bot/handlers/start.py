"""
Start and Registration handler for Sayohatchi Bot.
Manages onboarding for new users and instant access for registered users.
"""

import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from database import get_user, create_user, get_user_language
from translations import t
from keyboards import (
    get_main_menu_keyboard,
    get_language_keyboard,
    get_cancel_keyboard,
)

logger = logging.getLogger(__name__)

# Registration Conversation states
REG_CHOOSE_LANG, REG_FIRST_NAME, REG_LAST_NAME = range(3)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles /start command.
    If user is already registered, opens main menu directly.
    If new user, initiates language selection and registration flow.
    """
    user = update.effective_user
    if not user:
        return ConversationHandler.END

    telegram_id = user.id
    existing_user = get_user(telegram_id)

    if existing_user:
        lang = existing_user.get("language", "uz")
        name = existing_user.get("first_name", user.first_name)
        welcome_text = t("welcome_back", lang, name=name)
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(lang),
        )
        return ConversationHandler.END

    # New user onboarding:
    # 1. First display: "Assalomu alaykum. Xush kelibsiz!"
    welcome_text = t("welcome_new_user", "uz")
    await update.message.reply_text(welcome_text)

    # 2. Then ask to choose a language
    prompt = t("choose_language_prompt", "uz")
    await update.message.reply_text(
        prompt,
        reply_markup=get_language_keyboard(is_change=False, lang="uz"),
    )
    return REG_CHOOSE_LANG


async def reg_language_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handles language selection callback for new user registration."""
    query = update.callback_query
    await query.answer()

    data = query.data
    lang = "uz"
    if data == "set_lang_ru":
        lang = "ru"
    elif data == "set_lang_en":
        lang = "en"

    context.user_data["reg_language"] = lang

    # Ask for first name
    ask_name = t("ask_first_name", lang)
    await query.edit_message_text(ask_name)
    return REG_FIRST_NAME


async def reg_first_name_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Receives user's first name, validates, and asks for last name."""
    text = (update.message.text or "").strip()
    lang = context.user_data.get("reg_language", "uz")

    if not text or len(text) > 60:
        await update.message.reply_text(
            t("input_too_long" if len(text) > 60 else "invalid_input", lang),
            reply_markup=get_cancel_keyboard(lang),
        )
        return REG_FIRST_NAME

    context.user_data["reg_first_name"] = text
    await update.message.reply_text(
        t("ask_last_name", lang),
        reply_markup=get_cancel_keyboard(lang),
    )
    return REG_LAST_NAME


async def reg_last_name_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Receives user's last name, saves user to SQLite, and displays main menu."""
    text = (update.message.text or "").strip()
    lang = context.user_data.get("reg_language", "uz")
    first_name = context.user_data.get("reg_first_name", update.effective_user.first_name or "User")

    if not text or len(text) > 60:
        await update.message.reply_text(
            t("input_too_long" if len(text) > 60 else "invalid_input", lang),
            reply_markup=get_cancel_keyboard(lang),
        )
        return REG_LAST_NAME

    last_name = text
    telegram_id = update.effective_user.id

    # Persist user to SQLite database
    create_user(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        language=lang,
    )

    success_msg = t("registration_success", lang, name=first_name)
    await update.message.reply_text(
        success_msg,
        reply_markup=get_main_menu_keyboard(lang),
    )

    # Clean registration context
    context.user_data.pop("reg_language", None)
    context.user_data.pop("reg_first_name", None)

    return ConversationHandler.END


async def reg_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels registration flow."""
    user = update.effective_user
    lang = "uz"
    if user:
        lang = get_user_language(user.id)

    # Clean registration context
    context.user_data.pop("reg_language", None)
    context.user_data.pop("reg_first_name", None)

    msg = t("cancelled", lang)
    if update.message:
        await update.message.reply_text(msg, reply_markup=get_main_menu_keyboard(lang))
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg)

    return ConversationHandler.END


def get_registration_handler() -> ConversationHandler:
    """Returns the ConversationHandler for user registration."""
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            REG_CHOOSE_LANG: [
                CallbackQueryHandler(reg_language_callback, pattern="^set_lang_")
            ],
            REG_FIRST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, reg_first_name_handler)
            ],
            REG_LAST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, reg_last_name_handler)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", reg_cancel),
            MessageHandler(filters.Regex(r"^(❌ Bekor qilish|❌ Отмена|❌ Cancel)$"), reg_cancel),
        ],
        allow_reentry=True,
    )
