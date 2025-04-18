import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, 
    CommandHandler, 
    CallbackContext,
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes )

from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
EXCHANGE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
exchange_rates = {"timestamp": None, "rates": {}}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💵 Выбрать валюту", callback_data="select_currency")],
        [InlineKeyboardButton("ℹ️ О проекте", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🕌 *Ассаламу алейкум в Zakat Charity Token Calculator!*\n\n"
        "Я помогу рассчитать ваш обязательный закят на основе текущих курсов валют!\n"
        "Выберите действие:"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "select_currency":
        await select_currency(update, context)
    elif query.data == "about":
        await show_about(update, context)
    elif query.data.startswith("currency_"):
        selected_currency = query.data.split("_")[1]
        context.user_data["selected_currency"] = selected_currency
        await query.edit_message_text(
            f"✅ Выбрана валюта: {selected_currency}\n"
            "📥 Введите сумму активов:",
            parse_mode="Markdown"
        )

async def select_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    currencies = ["USD", "EUR", "GBP", "SAR", "TRY", "RUB", "KZT"]
    keyboard = [
        [InlineKeyboardButton(currency, callback_data=f"currency_{currency}")]
        for currency in currencies
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        "🌍 Выберите валюту:",
        reply_markup=reply_markup
    )

async def get_exchange_rates():
    if not exchange_rates["timestamp"] or datetime.now() - exchange_rates["timestamp"] > timedelta(hours=1):
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"
        )
        data = response.json()
        if data["result"] == "success":
            exchange_rates["rates"] = data["conversion_rates"]
            exchange_rates["timestamp"] = datetime.now()
    return exchange_rates["rates"]

async def calculate_zakat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text.replace(",", ".")
        amount = float(user_input)
        selected_currency = context.user_data.get("selected_currency", "USD")
        
        rates = await get_exchange_rates()
        amount_usd = amount / rates[selected_currency]
        
        zakat = amount_usd * 0.025
        nisab = 87.48
        
        zakat_local = zakat * rates[selected_currency]
        
        converted_zakat = {
            currency: round(zakat * rate, 2)
            for currency, rate in rates.items()
            if currency in ["USD", "EUR", "GBP", "SAR"]
        }
        
        response_text = (
            f"📊 *Результаты расчета:*\n\n"
            f"• Ваша сумма: {amount:.2f} {selected_currency}\n"
            f"• Закят (2.5%): {zakat_local:.2f} {selected_currency}\n"
            f"• Нисаб (мин. сумма): {nisab} г золота\n\n"
            "🌐 *Эквивалент в других валютах:*\n"
        )
        
        for currency, value in converted_zakat.items():
            response_text += f"  - {value:.2f} {currency}\n"
            
        response_text += "\n💡 Закят можно оплатить через наш благотворительный проект!"
        
        keyboard = [
            [InlineKeyboardButton("💸 Оплатить закят", url="https://your-charity-link.com")],
            [InlineKeyboardButton("🔄 Новый расчет", callback_data="select_currency")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await update.message.reply_text(
            "❌ Ошибка! Пожалуйста, введите корректную сумму числом.\n"
            "Пример: 15000 или 12345.67"
        )

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🌟 *Zakat Charity Token Project*\n\n"
        "Мы используем blockchain-технологии для:\n"
        "✅ Прозрачного распределения закята\n"
        "✅ Автоматического расчета нисаба\n"
        "✅ Мгновенных переводов между странами\n\n"
        "📈 Текущие курсы обновляются каждые 5 минут!\n"
        "🕋 2.5% от всех сборов идут на поддержку мечетей"
    )
    await update.callback_query.edit_message_text(
        about_text,
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_zakat))
    
    print("Бот запущен...")
    app.run_polling()
