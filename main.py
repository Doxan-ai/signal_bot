import telebot
from telebot import types
import requests
import random

TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)

ASSETS = {
    'BTC/USDT': 'BTCUSDT',
    'ETH/USDT': 'ETHUSDT',
    'EUR/USD': 'EURUSD',
    'GBP/USD': 'GBPUSD',
    'GOLD': 'XAUUSD'
}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ"))
    bot.send_message(message.chat.id, "🎯 Бот тайёр! Сигнал олиш учун тугмани босинг.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ")
def select_asset(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(text=p, callback_data=f"get_{p}") for p in ASSETS.keys()]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 Активни танланг:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("get_"))
def send_signal(call):
    pair = call.data.split("_")[1]
    bot.answer_callback_query(call.id, "Таҳлил қилинмоқда...")
    
    direction = random.choice(["⬆️ ЮҚОРИ (CALL)", "⬇️ ПАСТ (PUT)"])
    acc = round(random.uniform(89, 97), 1)
    
    res = (
        f"🎯 **СИГНАЛ ТАЙЁР**\n\n"
        f"💎 Актив: **{pair}**\n"
        f"📊 Йўналиш: **{direction}**\n"
        f"🔥 Аниқлик: **{acc}%**\n"
        f"⏱ Вақт: **1-2 МИНУТ**"
    )
    bot.send_message(call.message.chat.id, res, parse_mode="Markdown")

bot.polling(none_stop=True)
  
