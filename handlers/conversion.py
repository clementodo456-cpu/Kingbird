import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB
from database import record_conversion_result
from utils.files import create_user_temp_dir
from utils.cleanup import cleanup_directory
from converters.pdf_to_word import convert_pdf_to_word
from converters.pdf_to_images import convert_pdf_to_images
from converters.pdf_to_text import convert_pdf_to_text
from converters.word_to_pdf import convert_word_to_pdf
from converters.text_to_pdf import convert_text_to_pdf

async def prompt_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
    query = update.callback_query
    await query.answer()
    
    context.user_data["mode"] = mode
    prompts = {
        "conv_pdf_word": "📄 Please send the *PDF file* you want to convert to Word.",
        "conv_pdf_img": "🖼 Please send the *PDF file* you want to convert to Images.",
        "conv_pdf_txt": "📝 Please send the *PDF file* you want to extract text from.",
        "conv_word_pdf": "📑 Please send the *Word file (.doc / .docx)* you want to convert to PDF.",
        "conv_txt_pdf": "📃 Please send a *.txt file* or directly type/paste your text in the chat."
    }
    
    cancel_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="nav_main")]])
    await query.message.edit_text(prompts[mode], parse_mode="Markdown", reply_markup=cancel_kb)

async def handle_document_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if not mode or mode == "conv_img_pdf":
        return

    doc = update.message.document
    if not doc:
        return

    if doc.file_size > MAX_FILE_SIZE_BYTES:
        await update.message.reply_text(f"⚠️ File too large! Maximum limit is {MAX_FILE_SIZE_MB}MB.")
        return

    file_name = doc.file_name or "file"
    ext = os.path.splitext(file_name)[1].lower()

    # Extension validation
    valid_extensions = {
        "conv_pdf_word": [".pdf"],
        "conv_pdf_img": [".pdf"],
        "conv_pdf_txt": [".pdf"],
        "conv_word_pdf": [".doc", ".docx"],
        "conv_txt_pdf": [".txt"]
    }

    if ext not in valid_extensions.get(mode, []):
        await update.message.reply_text(f"⚠️ Invalid file type for this mode. Expected: {', '.join(valid_extensions[mode])}")
        return

    status_msg = await update.message.reply_text("⏳ Processing your file... Please wait.")
    temp_dir = create_user_temp_dir()

    try:
        tg_file = await context.bot.get_file(doc.file_id)
        input_path = os.path.join(temp_dir, file_name)
        await tg_file.download_to_drive(input_path)

        user_id = update.effective_user.id
        output_file = None

        if mode == "conv_pdf_word":
            output_file = os.path.join(temp_dir, "converted.docx")
            convert_pdf_to_word(input_path, output_file)
            caption = "📄 Your Word document is ready."

        elif mode == "conv_pdf_img":
            output_file = convert_pdf_to_images(input_path, temp_dir)
            caption = "🖼 Your image(s) are ready."

        elif mode == "conv_pdf_txt":
            output_file = os.path.join(temp_dir, "extracted_text.txt")
            convert_pdf_to_text(input_path, output_file)
            caption = "📝 Your extracted text file is ready."

        elif mode == "conv_word_pdf":
            output_file = convert_word_to_pdf(input_path, temp_dir)
            caption = "📑 Your PDF file is ready."

        elif mode == "conv_txt_pdf":
            output_file = os.path.join(temp_dir, "converted.pdf")
            with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            convert_text_to_pdf(content, output_file)
            caption = "📃 Your PDF file is ready."

        if output_file and os.path.exists(output_file):
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Convert Another", callback_data="nav_main")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="nav_main")]
            ])
            with open(output_file, "rb") as f:
                await update.message.reply_document(document=f, caption=f"✅ Conversion completed!\n{caption}", reply_markup=kb)
            record_conversion_result(user_id, success=True)
        else:
            raise RuntimeError("Generated file not found.")

    except Exception as e:
        record_conversion_result(update.effective_user.id, success=False)
        await update.message.reply_text("❌ Failed to process document. Please ensure it is not corrupted or password-protected.")
    finally:
        await status_msg.delete()
        cleanup_directory(temp_dir)
        context.user_data.clear()

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if mode != "conv_txt_pdf":
        return

    text_content = update.message.text
    if not text_content:
        return

    status_msg = await update.message.reply_text("⏳ Generating PDF... Please wait.")
    temp_dir = create_user_temp_dir()

    try:
        output_pdf = os.path.join(temp_dir, "text_document.pdf")
        convert_text_to_pdf(text_content, output_pdf)
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Convert Another", callback_data="nav_main")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="nav_main")]
        ])
        with open(output_pdf, "rb") as f:
            await update.message.reply_document(document=f, caption="✅ Conversion completed!\n📃 Your PDF file is ready.", reply_markup=kb)
        record_conversion_result(update.effective_user.id, success=True)
    except Exception:
        record_conversion_result(update.effective_user.id, success=False)
        await update.message.reply_text("❌ Failed to generate PDF from text.")
    finally:
        await status_msg.delete()
        cleanup_directory(temp_dir)
        context.user_data.clear()
