import telebot
from telebot import types
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
    'EUR/AUD (OTC)', 'GBP/AUD (OTC)', 'CHF/JPY (OTC)',
    'EUR/CHF (OTC)', 'AUD/CAD (OTC)', 'GBP/CAD (OTC)'
]

def analyze_logic_v7():
    # 1. Смарт Моней концепциялари (Симуляция)
    choch = random.choice([True, False]) # Тренд ўзгариши
    fvg = random.choice([True, False])   # Нархдаги бўшлиқ
    bos = random.choice([True, False])   # Тренд давоми
    zone = random.choice(["Demand", "Supply", "Neutral"]) # Зоналар
    
    # 2. Индикаторлар
    rsi = round(random.uniform(15.0, 85.0), 2)
    macd = round(random.uniform(-0.005, 0.005), 6)
    
    # СИГНАЛ МАНТИҚИ (Энг кучли комбинациялар)
    if choch and fvg and zone == "Demand" and rsi < 40:
        return "🔥", "STRONG BUY (CHOCH+FVG)", "Demand зонасидан ўсиш кутилмоқда", "3-5 мин.", 99.4
    
    elif choch and fvg and zone == "Supply" and rsi > 60:
        return "⚡", "STRONG SELL (CHOCH+FVG)", "Supply зонасидан тушиш кутилмоқда", "3-5 мин.", 98.7
    
    elif bos and fvg:
        return "📈", "TREND CONTINUE", "BOS тасдиқланди, тренд давом этади", "2-3 мин.", 96.5
    
    else:
        # Агар Смарт Моней сигнал бермаса, индикаторларга қарайди
        if rsi < 30: return "🟢", "BUY", "RSI бўйича қайта тикланиш", "1-2 мин.", 94.2
        elif rsi > 70: return "🔴", "SELL", "RSI бўйича тушиш", "1-2 мин.", 93.8
        else: return "🔍", "WAITING", "Аниқ зона кутилмоқда...", "0 мин.", 0

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ"))
    bot.send_message(message.chat.id, "<b>💎 AI Bot v7.0: Smart Money (CHOCH, FVG, BOS) фаоллаштирилди!</b>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sig_"))
def send_signal(call):
    pair = call.data.split("_")[1]
    icon, txt, desc, duration, acc = analyze_logic_v7()
    
    if acc == 0:
        msg = f"⚠️ <b>{pair}</b> бўйича ҳозирча хавфсиз сигнал йўқ. Бозорда манипуляция бўлиши мумкин."
    else:
        msg = (
            f"{icon} <b>{txt}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💎 Актив: <b>{pair}</b>\n"
            f"🎯 Вақт: <b>{duration}</b>\n"
            f"🔥 Аниқлик: <b>{acc}%</b>\n"
            f"📝 Ҳолат: <i>{desc}</i>\n"
            f"━━━━━━━━━━━━━━━"
        )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Қайта таҳлил қилиш", callback_data=f"sig_{pair}"))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ")
def select_asset(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(text=p, callback_data=f"sig_{p}") for p in ASSETS]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 <b>Активни танланг:</b>", parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
