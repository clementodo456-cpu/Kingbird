import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import MAX_FILE_SIZE_BYTES
from database import record_conversion_result
from utils.files import create_user_temp_dir
from utils.cleanup import cleanup_directory
from converters.images_to_pdf import convert_images_to_pdf

async def prompt_images_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    context.user_data["mode"] = "conv_img_pdf"
    context.user_data["images"] = []
    context.user_data["temp_dir"] = create_user_temp_dir()

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="nav_main")]])
    await query.message.edit_text(
        "🖼 Please send your image(s) (JPG/PNG) one by one or as a batch.\n\n"
        "When finished, click *✅ Create PDF* below.",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def collect_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("mode") != "conv_img_pdf":
        return

    photo = update.message.photo[-1] if update.message.photo else None
    doc = update.message.document if update.message.document and update.message.document.mime_type.startswith("image/") else None

    if not photo and not doc:
        return

    file_id = photo.file_id if photo else doc.file_id
    file_size = photo.file_size if photo else doc.file_size

    if file_size > MAX_FILE_SIZE_BYTES:
        await update.message.reply_text("⚠️ Image file is too large!")
        return

    temp_dir = context.user_data.get("temp_dir")
    if not temp_dir or not os.path.exists(temp_dir):
        temp_dir = create_user_temp_dir()
        context.user_data["temp_dir"] = temp_dir

    img_index = len(context.user_data.get("images", [])) + 1
    file_path = os.path.join(temp_dir, f"img_{img_index}.jpg")

    tg_file = await context.bot.get_file(file_id)
    await tg_file.download_to_drive(file_path)

    context.user_data.setdefault("images", []).append(file_path)
    count = len(context.user_data["images"])

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ Create PDF ({count})", callback_data="process_img_pdf")],
        [InlineKeyboardButton("❌ Cancel", callback_data="nav_main")]
    ])
    await update.message.reply_text(f"📷 Image #{count} received!", reply_markup=kb)

async def process_images_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    images = context.user_data.get("images", [])
    temp_dir = context.user_data.get("temp_dir")

    if not images:
        await query.message.reply_text("⚠️ No images collected yet. Please send images first.")
        return

    status_msg = await query.message.reply_text("⏳ Generating PDF from images... Please wait.")

    try:
        output_pdf = os.path.join(temp_dir, "combined_images.pdf")
        convert_images_to_pdf(images, output_pdf)

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Convert Another", callback_data="nav_main")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="nav_main")]
        ])
        with open(output_pdf, "rb") as f:
            await query.message.reply_document(document=f, caption="✅ PDF generated successfully from images!", reply_markup=kb)
        record_conversion_result(update.effective_user.id, success=True)
    except Exception:
        record_conversion_result(update.effective_user.id, success=False)
        await query.message.reply_text("❌ Failed to create PDF from images.")
    finally:
        await status_msg.delete()
        cleanup_directory(temp_dir)
        context.user_data.clear()
