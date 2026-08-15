import logging
import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config import BOT_TOKEN
from database import init_db
from handlers.start import start_command, help_command, cancel_command
from handlers.conversion import prompt_conversion, handle_document_conversion, handle_text_message
from handlers.images import prompt_images_to_pdf, collect_image, process_images_to_pdf
from handlers.admin import (
    admin_command,
    admin_users_command,
    admin_botstats_command,
    admin_broadcast_command,
    user_stats_command
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    # Initialize SQLite Database
    init_db()

    # Build Telegram Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CommandHandler("stats", user_stats_command))

    # Admin Command Handlers
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("users", admin_users_command))
    application.add_handler(CommandHandler("botstats", admin_botstats_command))
    application.add_handler(CommandHandler("broadcast", admin_broadcast_command))

    # Callback Handlers
    application.add_handler(CallbackQueryHandler(start_command, pattern="^nav_main$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^nav_help$"))
    application.add_handler(CallbackQueryHandler(prompt_images_to_pdf, pattern="^conv_img_pdf$"))
    application.add_handler(CallbackQueryHandler(process_images_to_pdf, pattern="^process_img_pdf$"))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: prompt_conversion(u, c, u.callback_query.data),
        pattern="^conv_(pdf_word|pdf_img|pdf_txt|word_pdf|txt_pdf)$"
    ))

    # Message Handlers
    application.add_handler(MessageHandler(filters.PHOTO | (filters.Document.IMAGE), collect_image))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document_conversion))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    # Start Long Polling
    logger.info("Starting bot in long-polling mode...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
