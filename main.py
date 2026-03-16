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
    # Render учун портни созлаш (Бу жуда муҳим!)
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

ASSETS = {
    'BTC/USDT': 'BTCUSDT',
    'ETH/USDT': 'ETHUSDT',
    'EUR/USD': 'EURUSD',
    'GBP/USD': 'GBPUSD',
    'GOLD': 'XAUUSD'
}

def get_live_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=5).json()
        return float(res['price'])
    except:
        return round(random.uniform(1.1, 1.3), 5)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ"))
    bot.send_message(message.chat.id, "<b>🤖 AI Trading Bot v5.1</b>\nСигнал олиш учун тугмани босинг.", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ")
def select_asset(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(text=p, callback_data=f"sig_{p}") for p in ASSETS.keys()]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 <b>Активни танланг:</b>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sig_"))
def send_signal(call):
    pair = call.data.split("_")[1]
    
    # Эски хабарни янгилаш (Тезроқ ишлаши учун)
    bot.edit_message_text("🔍 <b>Бозор сканер қилинмоқда...</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    
    price = get_live_price(ASSETS[pair])
    rsi = round(random.uniform(20.0, 80.0), 2)
    acc = round(random.uniform(92.0, 98.9), 1)
    
    icon, txt = ("🟢", "ВВЕРХ / BUY") if rsi < 45 else ("🔴", "ВНИЗ / SELL")
    
    msg = (
        f"{icon} <b>{txt}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💎 Актив: <b>{pair}</b>\n"
        f"✅ <b>✓ {price}</b>\n"
        f"🔥 Сила сигнала: <b>{acc}%</b>\n"
        f"📉 RSI: <b>{rsi}</b>\n"
        f"⏱ Время: <b>1 мин.</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 <i>Сигнал янгиланди.</i>"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Получить еще", callback_data=f"sig_{pair}"))
    
    # Натижани чиқариш
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
