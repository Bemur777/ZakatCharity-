import logging
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Настройка логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Этапы диалога
INPUT_SAVINGS, INPUT_GOLD, INPUT_SILVER, INPUT_DEBT = range(4)
NISAB = 5000  # Уточните актуальный нисаб для вашей валюты

async def start(update: Update, context):
    await update.message.reply_text(
        "🕌 Ассаляму алейкум! Я помогу рассчитать закят.\n"
        "Введите ваши сбережения в валюте:"
    )
    return INPUT_SAVINGS

async def input_savings(update: Update, context):
    try:
        savings = float(update.message.text.replace(",", "."))
        context.user_data['savings'] = savings
        await update.message.reply_text("Введите стоимость золота (в валюте), если нет — 0:")
        return INPUT_GOLD
    except ValueError:
        await update.message.reply_text("❌ Ошибка! Введите число.")
        return INPUT_SAVINGS

async def input_gold(update: Update, context):
    try:
        gold = float(update.message.text.replace(",", "."))
        context.user_data['gold'] = gold
        await update.message.reply_text("Введите стоимость серебра (в валюте), если нет — 0:")
        return INPUT_SILVER
    except ValueError:
        await update.message.reply_text("❌ Ошибка! Введите число.")
        return INPUT_GOLD

async def input_silver(update: Update, context):
    try:
        silver = float(update.message.text.replace(",", "."))
        context.user_data['silver'] = silver
        await update.message.reply_text("Введите сумму долгов (в валюте), если нет — 0:")
        return INPUT_DEBT
    except ValueError:
        await update.message.reply_text("❌ Ошибка! Введите число.")
        return INPUT_SILVER

async def input_debt(update: Update, context):
    try:
        debt = float(update.message.text.replace(",", "."))
        total = (
            context.user_data['savings'] 
            + context.user_data['gold'] 
            + context.user_data['silver']
        ) - debt

        if total < NISAB:
            await update.message.reply_text("📉 Закят не обязателен: сумма ниже нисаба.")
        else:
            zakat = total * 0.025
            await update.message.reply_text(
                f"📌 Сумма закята: {zakat:.2f}.\n"
                "Не забудьте учесть другие условия выплаты закята!"
            )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("❌ Ошибка! Введите число.")
        return INPUT_DEBT

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INPUT_SAVINGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_savings)],
            INPUT_GOLD: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_gold)],
            INPUT_SILVER: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_silver)],
            INPUT_DEBT: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_debt)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
