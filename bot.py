import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config import BOT_TOKEN, WEBHOOK_URL
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

# Initialize Application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Register Handlers
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("cancel", cancel_command))
telegram_app.add_handler(CommandHandler("stats", user_stats_command))

telegram_app.add_handler(CommandHandler("admin", admin_command))
telegram_app.add_handler(CommandHandler("users", admin_users_command))
telegram_app.add_handler(CommandHandler("botstats", admin_botstats_command))
telegram_app.add_handler(CommandHandler("broadcast", admin_broadcast_command))

# Callbacks
telegram_app.add_handler(CallbackQueryHandler(start_command, pattern="^nav_main$"))
telegram_app.add_handler(CallbackQueryHandler(help_command, pattern="^nav_help$"))
telegram_app.add_handler(CallbackQueryHandler(prompt_images_to_pdf, pattern="^conv_img_pdf$"))
telegram_app.add_handler(CallbackQueryHandler(process_images_to_pdf, pattern="^process_img_pdf$"))
telegram_app.add_handler(CallbackQueryHandler(
    lambda u, c: prompt_conversion(u, c, u.callback_query.data),
    pattern="^conv_(pdf_word|pdf_img|pdf_txt|word_pdf|txt_pdf)$"
))

# Messages
telegram_app.add_handler(MessageHandler(filters.PHOTO | (filters.Document.IMAGE), collect_image))
telegram_app.add_handler(MessageHandler(filters.Document.ALL, handle_document_conversion))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await telegram_app.initialize()
    await telegram_app.start()

    if WEBHOOK_URL:
        full_webhook_url = f"{WEBHOOK_URL}/webhook"
        logger.info(f"Setting webhook to: {full_webhook_url}")
        await telegram_app.bot.set_webhook(url=full_webhook_url)

    yield

    logger.info("Stopping Telegram Application...")
    await telegram_app.stop()
    await telegram_app.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/webhook")
async def process_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return Response(status_code=200)
