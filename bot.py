import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота (хранится в .env)
TOKEN = os.getenv("BOT_TOKEN")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🕌 Добро пожаловать в калькулятор закята! Введите сумму активов:")

# Обработчик текстовых сообщений (расчет закята)
async def calculate_zakat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text)
        zakat = amount * 0.025  # 2.5% от суммы
        await update.message.reply_text(f"📉 Размер закята: **{zakat:.2f}** ₽", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Ошибка! Введите корректную сумму.")

# Настройка и запуск бота
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_zakat))
    
    print("Бот запущен...")
    app.run_polling()
