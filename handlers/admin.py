from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import get_global_stats, get_user_stats, get_all_user_ids

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

async def user_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_user_stats(user_id)
    text = (
        f"📊 *Your Statistics*\n\n"
        f"✅ Successful Conversions: `{stats['success']}`\n"
        f"❌ Failed Conversions: `{stats['failed']}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    text = (
        "👑 *Admin Dashboard*\n\n"
        "Available Admin Commands:\n"
        "• /users - Show total registered users\n"
        "• /botstats - Global conversion statistics\n"
        "• /broadcast <message> - Broadcast a message to all users"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def admin_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    stats = get_global_stats()
    await update.message.reply_text(f"👥 Total registered users: `{stats['total_users']}`", parse_mode="Markdown")

async def admin_botstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    stats = get_global_stats()
    text = (
        f"📈 *Global Bot Statistics*\n\n"
        f"👥 Total Users: `{stats['total_users']}`\n"
        f"✅ Total Successful Conversions: `{stats['total_success']}`\n"
        f"❌ Total Failed Conversions: `{stats['total_failed']}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/broadcast <your message>`", parse_mode="Markdown")
        return

    broadcast_text = " ".join(context.args)
    users = get_all_user_ids()
    sent_count = 0

    for u_id in users:
        try:
            await context.bot.send_message(chat_id=u_id, text=f"📢 *Announcement*\n\n{broadcast_text}", parse_mode="Markdown")
            sent_count += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {sent_count}/{len(users)} users.")
