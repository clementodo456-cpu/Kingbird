from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import log_user

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📄 PDF → Word", callback_data="conv_pdf_word"), InlineKeyboardButton("🖼 PDF → Images", callback_data="conv_pdf_img")],
        [InlineKeyboardButton("📝 PDF → Text", callback_data="conv_pdf_txt"), InlineKeyboardButton("📑 Word → PDF", callback_data="conv_word_pdf")],
        [InlineKeyboardButton("🖼 Images → PDF", callback_data="conv_img_pdf"), InlineKeyboardButton("📃 Text → PDF", callback_data="conv_txt_pdf")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="nav_help")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user(user.id, user.username or user.first_name)
    context.user_data.clear()

    text = (
        f"👋 *Welcome to @KingBirdPrekChakSBS24bot!*\n\n"
        f"I am your all-in-one document conversion assistant. "
        f"Select an option below to convert your files quickly and securely."
    )
    
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ *Bot Help & Instructions*\n\n"
        "• *Supported Conversions:*\n"
        "  - PDF → Word (.docx)\n"
        "  - PDF → Images (.jpg / .zip)\n"
        "  - PDF → Text (.txt)\n"
        "  - Word → PDF (.doc / .docx)\n"
        "  - Images → PDF (JPG, PNG)\n"
        "  - Text → PDF (Send text or .txt file)\n\n"
        "• *Limitations:*\n"
        "  - Maximum file size: 20MB\n"
        "  - Password-protected PDFs are not supported.\n\n"
        "• *Commands:*\n"
        "  /start - Main menu\n"
        "  /help - Display help\n"
        "  /cancel - Cancel active process\n"
        "  /stats - Your personal conversion stats"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="nav_main")]])
    
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    elif update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    text = "❌ Current operation cancelled."
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="nav_main")]])
    await update.message.reply_text(text, reply_markup=keyboard)
