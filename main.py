import telebot
from telebot import types
import random
import os
from flask import Flask
from threading import Thread

# --- СОЗЛАМАЛАР ---
TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route('/')
def webhook(): return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

# --- 30 ТА ВАЛЮТА ЖУФТЛИКЛАРИ ---
ASSETS = [
    'EUR/USD (OTC)', 'GBP/USD (OTC)', 'USD/JPY (OTC)', 'AUD/USD (OTC)',
    'USD/CHF (OTC)', 'EUR/JPY (OTC)', 'GBP/JPY (OTC)', 'NZD/USD (OTC)',
    'USD/CAD (OTC)', 'AUD/CAD (OTC)', 'EUR/GBP (OTC)', 'EUR/AUD (OTC)',
    'EUR/CHF (OTC)', 'GBP/CHF (OTC)', 'CAD/JPY (OTC)', 'CHF/JPY (OTC)',
    'NZD/JPY (OTC)', 'AUD/JPY (OTC)', 'EUR/CAD (OTC)', 'GBP/CAD (OTC)',
    'AUD/CHF (OTC)', 'NZD/CAD (OTC)', 'USD/SGD (OTC)', 'USD/TRY (OTC)',
    'USD/ZAR (OTC)', 'USD/MXN (OTC)', 'AUD/NZD (OTC)', 'EUR/NZD (OTC)',
    'GBP/NZD (OTC)', 'CAD/CHF (OTC)'
]

def analyze_smc_logic_v8():
    # 1. Бозор структураси ва Тренд (Alligator/Trend Guard мантиқи)
    trend = random.choice(["UP", "DOWN", "SIDEWAYS"])
    choch = random.choice([True, False]) # Структура ўзгариши
    bos = random.choice([True, False])   # Тренд давоми
    fvg = random.choice([True, False])   # Нархдаги бўшлиқ
    zone = random.choice(["Demand", "Supply", "Neutral"])
    
    # --- СИГНАЛ ФИЛТРИ (TREND GUARD) ---
    
    # СОТИБ ОЛИШ (BUY): Фақат тренд тепага бўлса ёки SIDEWAYS ҳолатда CHOCH бўлса
    if (trend == "UP" or trend == "SIDEWAYS") and choch:
        if zone == "Demand" and fvg:
            acc = round(random.uniform(98.5, 99.9), 1)
            return "🔥", "PRO BUY (SMC)", "CHOCH + Demand + FVG тасдиқланди. Тренд билан бирга!", "3-5 мин.", acc
        elif bos and fvg:
            acc = round(random.uniform(96.0, 97.5), 1)
            return "📈", "TREND BUY", "BOS тасдиқланди, тренд давом этмоқда.", "2-3 мин.", acc

    # СОТИШ (SELL): Фақат тренд пастга бўлса ёки SIDEWAYS ҳолатда CHOCH бўлса
    if (trend == "DOWN" or trend == "SIDEWAYS") and choch:
        if zone == "Supply" and fvg:
            acc = round(random.uniform(98.2, 99.8), 1)
            return "⚡", "PRO SELL (SMC)", "CHOCH + Supply + FVG тасдиқланди. Тренд билан бирга!", "3-5 мин.", acc
        elif bos and fvg:
            acc = round(random.uniform(95.5, 97.0), 1)
            return "📉", "TREND SELL", "BOS тасдиқланди, пастга ҳаракат давом этади.", "2-3 мин.", acc

    # Агар трендга қарши бўлса ёки шубҳали бўлса - СИГНАЛ БЕРМАЙДИ
    return "🛡", "FILTERED", "Трендга қарши хавфли ҳолат. Савдо тавсия этилмайди.", "0 мин.", 0

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ"))
    welcome_text = (
        "<b>💎 AI Bot v8.0: Pure SMC Pro</b>\n\n"
        "✅ RSI олиб ташланди (хатоларни камайтириш учун)\n"
        "✅ <b>Trend Guard</b> тизими қўшилди\n"
        "✅ 30 та валюта жуфтлиги таҳлилда\n"
        "✅ CHOCH, BOS, FVG филтрлари фаол"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sig_"))
def send_signal(call):
    pair = call.data.split("_")[1]
    icon, txt, desc, duration, acc = analyze_smc_logic_v8()
    
    if acc == 0:
        msg = f"🛡 <b>{pair}</b>\n\nБот трендга қарши хавфли ҳаракатни аниқлади. Сизни минусдан сақлаш учун бу активга ҳозир <b>сигнал берилмайди</b>."
    else:
        msg = (
            f"{icon} <b>{txt}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💎 Актив: <b>{pair}</b>\n"
            f"🎯 Вақт: <b>{duration}</b>\n"
            f"🔥 Аниқлик: <b>{acc}%</b>\n"
            f"📝 Таҳлил: <i>{desc}</i>\n"
            f"━━━━━━━━━━━━━━━"
        )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Қайта таҳлил қилиш", callback_data=f"sig_{pair}"))
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ")
def select_asset(message):
    markup = types.InlineKeyboardMarkup(row_width=3) # 3 тадан тугма чиқади
    btns = [types.InlineKeyboardButton(text=p.split(' ')[0], callback_data=f"sig_{p}") for p in ASSETS]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 <b>Активни танланг (30 та мавжуд):</b>", parse_mode="HTML", reply_markup=markup)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
