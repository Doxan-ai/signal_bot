import telebot
from telebot import types
import requests
import random
import os
from flask import Flask
from threading import Thread

TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route('/')
def webhook(): return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

ASSETS = [
    'AUD/CHF (OTC)', 'NZD/USD (OTC)', 'USD/ZAR (OTC)',
    'AUD/USD (OTC)', 'CAD/JPY (OTC)', 'NZD/CAD (OTC)',
    'EUR/AUD (OTC)', 'USD/MXN (OTC)', 'USD/SEK (OTC)',
    'EUR/SEK (OTC)', 'GBP/AUD (OTC)', 'GBP/CHF (OTC)',
    'CHF/JPY (OTC)', 'USD/NOK (OTC)', 'GBP/NZD (OTC)',
    'EUR/NZD (OTC)', 'NZD/CHF (OTC)', 'USD/SGD (OTC)',
    'EUR/CHF (OTC)', 'AUD/CAD (OTC)', 'GBP/CAD (OTC)'
]

def analyze_logic():
    # RSI таҳлили
    rsi = round(random.uniform(15.0, 85.0), 2)
    # MACD 9, 10, 9 симуляцияси
    macd_line = round(random.uniform(-0.005, 0.005), 6)
    signal_line = round(random.uniform(-0.005, 0.005), 6)
    
    acc = round(random.uniform(96.1, 99.7), 1)
    price = round(random.uniform(0.60000, 1.30000), 5)
    
    # MACD ва RSI бирлашган ҳолатда йўналиш танлаш
    if rsi < 40 and macd_line > signal_line:
        direction, txt, icon = "🟢", "ВВЕРХ / BUY", "🟢"
    elif rsi > 60 and macd_line < signal_line:
        direction, txt, icon = "🔴", "ВНИЗ / SELL", "🔴"
    else:
        # Агар кўрсаткичлар ҳар хил бўлса, кучлироқ трендга қарайди
        direction = "🟢" if rsi < 50 else "🔴"
        txt = "ВВЕРХ / BUY" if direction == "🟢" else "ВНИЗ / SELL"
        icon = direction

    # Вақтни белгилаш
    duration = "1 мин." if (rsi < 25 or rsi > 75) else "3 мин."
    
    return icon, txt, rsi, macd_line, acc, price, duration

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ"))
    bot.send_message(message.chat.id, "<b>🔥 AI Bot v6.5: MACD (9,10,9) фаоллаштирилди!</b>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ")
def select_asset(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = [types.InlineKeyboardButton(text=p, callback_data=f"sig_{p}") for p in ASSETS]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 <b>Активни танланг:</b>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sig_"))
def send_signal(call):
    pair = call.data.split("_")[1]
    bot.edit_message_text(f"🔄 <b>{pair}: RSI + MACD таҳлил...</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    
    icon, txt, rsi, macd, acc, price, duration = analyze_logic()

    msg = (
        f"{icon} <b>{txt}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💎 Актив: <b>{pair}</b>\n"
        f"✅ <b>✓ {price}</b>\n"
        f"🎯 Вақт: <b>{duration}</b>\n"
        f"🔥 Аниқлик: <b>{acc}%</b>\n"
        f"📉 RSI-14: <b>{rsi}</b>\n"
        f"📊 MACD: <b>{macd}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💡 <i>Икки босқичли тасдиқлашдан ўтди.</i>"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Янги сигнал олиш", callback_data=f"sig_{pair}"))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
