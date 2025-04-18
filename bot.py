import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
EXCHANGE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

# Currency rates cache
exchange_rates = {"timestamp": None, "rates": {}}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button presses"""
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

async def select_currency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show currency selection menu"""
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

async def get_exchange_rates() -> dict:
    """Fetch and cache currency rates"""
    if not exchange_rates["timestamp"] or datetime.now() - exchange_rates["timestamp"] > timedelta(hours=1):
        response = requests.get(
            f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"
        )
        data = response.json()
        if data["result"] == "success":
            exchange_rates["rates"] = data["conversion_rates"]
            exchange_rates["timestamp"] = datetime.now()
    return exchange_rates["rates"]

async def calculate_zakat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Calculate zakat amount"""
    try:
        user_input = update.message.text.replace(",", ".")
        amount = float(user_input)
        selected_currency = context.user_data.get("selected_currency", "USD")
        
        rates = await get_exchange_rates()
        if selected_currency not in rates:
            raise ValueError("Unsupported currency")
        
        amount_usd = amount / rates[selected_currency]
        zakat = amount_usd * 0.025
        nisab = 87.48  # Gold nisab in grams
        
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
        
        response_text += "\n".join([f"  - {value:.2f} {currency}" for currency, value in converted_zakat.items()])
        response_text += "\n\n💡 Закят можно оплатить через наш благотворительный проект!"
        
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
        
    except ValueError:
        await update.message.reply_text(
            "❌ Ошибка! Пожалуйста, введите корректную сумму числом.\n"
            "Пример: 15000 или 12345.67"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Произошла ошибка: {str(e)}")

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show project information"""
    about_text = (
        "🌟 *Zakat Charity Token Project*\n\n"
        "Мы используем blockchain-технологии для:\n"
        "✅ Прозрачного распределения закята\n"
        "✅ Автоматического расчета нисаба\n"
        "✅ Мгновенных переводов между странами\n\n"
        "📈 Текущие курсы
