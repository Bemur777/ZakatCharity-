from telegram import Update
from telegram.ext import ContextTypes

async def invite_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    invite_link = f"https://t.me/your_bot_username?start=ref_{user.id}"
    
    text = (
        "🎉 *Ваша реферальная ссылка:*\n"
        f"`{invite_link}`\n\n"
        "Пригласите друзей и получайте бонусы!"
    )
    
    await update.message.reply_text(text, parse_mode="Markdown")

def handle_referral(context_args: list):
    if context_args and context_args[0].startswith("ref_"):
        ref_id = context_args[0].split("_")[1]
        return ref_id
    return None

def save_referral(referrer_id: int, user_id: int):
    with open("referrals.txt", "a") as f:
        f.write(f"Реферал: {user_id}, Пригласил: {referrer_id}\n")
