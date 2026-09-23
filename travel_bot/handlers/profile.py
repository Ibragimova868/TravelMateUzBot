"""
User profile management handler for Sayohatchi Bot.
Displays user information from SQLite and permits editing names and language.
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
from database import (
    get_user,
    update_user_name,
    get_user_language,
)
from translations import t, get_language_display_name
from keyboards import (
    get_profile_keyboard,
    get_cancel_keyboard,
    get_main_menu_keyboard,
    get_language_keyboard,
)

logger = logging.getLogger(__name__)

# Profile Edit States
EDIT_FIRST_NAME, EDIT_LAST_NAME = range(2)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches user details from database and renders profile card."""
    user = update.effective_user
    if not user:
        return

    telegram_id = user.id
    db_user = get_user(telegram_id)
    lang = db_user.get("language", "uz") if db_user else "uz"

    first_name = db_user.get("first_name", user.first_name or "Noma'lum") if db_user else user.first_name
    last_name = db_user.get("last_name", user.last_name or "-") if db_user else "-"
    raw_created_at = db_user.get("created_at") if db_user else None
    
    # Format registration date into DD.MM.YYYY directly from SQLite timestamp
    formatted_date = ""
    if raw_created_at:
        try:
            date_part = str(raw_created_at).strip().split()[0]
            parts = date_part.split("-")
            if len(parts) == 3:
                formatted_date = f"{parts[2]}.{parts[1]}.{parts[0]}"
            else:
                formatted_date = date_part
        except Exception:
            formatted_date = str(raw_created_at)

    lang_display = get_language_display_name(lang)

    text = t(
        "profile_title",
        lang,
        first_name=first_name,
        last_name=last_name,
        language=lang_display,
        created_at=formatted_date,
    )

    keyboard = get_profile_keyboard(lang)

    if update.message:
        await update.message.reply_text(text, reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=keyboard)


async def edit_name_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Starts the edit name conversation."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"

    await query.edit_message_text(t("ask_new_first_name", lang))
    return EDIT_FIRST_NAME


async def edit_first_name_received(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Receives new first name and asks for new last name."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    text = (update.message.text or "").strip()

    if text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "🔙 Orqaga", "🔙 Назад", "🔙 Back"]:
        await update.message.reply_text(
            t("cancelled", lang), reply_markup=get_main_menu_keyboard(lang)
        )
        return ConversationHandler.END

    if not text or len(text) > 60:
        await update.message.reply_text(
            t("input_too_long" if len(text) > 60 else "invalid_input", lang),
            reply_markup=get_cancel_keyboard(lang),
        )
        return EDIT_FIRST_NAME

    context.user_data["edit_first_name"] = text
    await update.message.reply_text(
        t("ask_new_last_name", lang), reply_markup=get_cancel_keyboard(lang)
    )
    return EDIT_LAST_NAME


async def edit_last_name_received(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Receives new last name, updates SQLite, and shows updated profile."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    text = (update.message.text or "").strip()

    if text in ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel", "🔙 Orqaga", "🔙 Назад", "🔙 Back"]:
        await update.message.reply_text(
            t("cancelled", lang), reply_markup=get_main_menu_keyboard(lang)
        )
        return ConversationHandler.END

    if not text or len(text) > 60:
        await update.message.reply_text(
            t("input_too_long" if len(text) > 60 else "invalid_input", lang),
            reply_markup=get_cancel_keyboard(lang),
        )
        return EDIT_LAST_NAME

    new_first = context.user_data.get("edit_first_name", user.first_name)
    new_last = text

    update_user_name(user.id, new_first, new_last)

    await update.message.reply_text(
        t("name_updated_success", lang),
        reply_markup=get_main_menu_keyboard(lang),
    )

    # Show updated profile
    await show_profile(update, context)

    context.user_data.pop("edit_first_name", None)
    return ConversationHandler.END


async def edit_name_cancel(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Cancels name edit flow."""
    user = update.effective_user
    lang = get_user_language(user.id) if user else "uz"
    context.user_data.pop("edit_first_name", None)

    msg = t("cancelled", lang)
    if update.message:
        await update.message.reply_text(msg, reply_markup=get_main_menu_keyboard(lang))
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(msg)

    return ConversationHandler.END


def get_profile_handler() -> ConversationHandler:
    """Returns conversation handler for editing profile name."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(edit_name_start, pattern="^prof_edit_name$")
        ],
        states={
            EDIT_FIRST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_first_name_received)
            ],
            EDIT_LAST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_last_name_received)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", edit_name_cancel),
            MessageHandler(
                filters.Regex(r"^(❌ Bekor qilish|❌ Отмена|❌ Cancel|🔙 Orqaga|🔙 Назад|🔙 Back)$"),
                edit_name_cancel,
            ),
        ],
        allow_reentry=True,
    )
