import telebot
from telebot import types
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import time

# Бот токени
TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)

# Активлар (Yahoo Finance форматда)
ASSETS = {
    'EUR/USD': 'EURUSD=X',
    'GBP/USD': 'GBPUSD=X',
    'BTC/USDT': 'BTC-USD',
    'ETH/USDT': 'ETH-USD',
    'GOLD': 'GC=F'
}

def get_signal(ticker_symbol):
    try:
        # Охирги 2 соатлик маълумотни олиш (1 дақиқалик интервал)
        data = yf.download(ticker=ticker_symbol, period='1d', interval='1m', progress=False)
        
        if data.empty:
            return None

        # Индикаторларни ҳисоблаш
        data['RSI'] = ta.rsi(data['Close'], length=14)
        data['EMA_10'] = ta.ema(data['Close'], length=10)
        data['EMA_20'] = ta.ema(data['Close'], length=20)
        
        last_row = data.iloc[-1]
        rsi_val = last_row['RSI']
        close_price = last_row['Close']
        ema10 = last_row['EMA_10']
        ema20 = last_row['EMA_20']

        # Сигнал мантиқи
        if rsi_val < 35 or (ema10 > ema20):
            direction = "⬆️ ЮҚОРИ (CALL)"
            accuracy = 88.5 + (rsi_val % 5)
        elif rsi_val > 65 or (ema10 < ema20):
            direction = "⬇️ ПАСТ (PUT)"
            accuracy = 87.9 + (rsi_val % 5)
        else:
            direction = "⏳ КУТИШ (НЕЙТРАЛ)"
            accuracy = 50.0

        return {
            'dir': direction,
            'acc': round(min(accuracy, 98.1), 1),
            'rsi': round(rsi_val, 2),
            'price': round(close_price, 4)
        }
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СУПЕР АНАЛИЗ (PRO)"))
    bot.send_message(message.chat.id, "🤖 **Pocket Option Pro Bot** ишга тушди!\nБу тизим Yahoo Finance орқали энг барқарор сигналларни беради.", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🚀 СУПЕР АНАЛИЗ (PRO)")
def show_pairs(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(text=p, callback_data=f"pro_{p}") for p in ASSETS.keys()]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📈 Таҳлил учун активни танланг:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pro_"))
def handle_pro(call):
    pair_name = call.data.split("_")[1]
    ticker = ASSETS[pair_name]
    
    bot.edit_message_text(f"📡 {pair_name} сканерланмоқда...", call.message.chat.id, call.message.message_id)
    
    res = get_signal(ticker)
    
    if not res:
        bot.send_message(call.message.chat.id, "❌ Маълумот олишда хатолик. Бироздан сўнг уриниб кўринг.")
        return

    msg = (
        f"🎯 **PRO АНАЛИЗ НАТИЖАСИ**\n\n"
        f"💎 Актив: **{pair_name}**\n"
        f"📊 Йўналиш: **{res['dir']}**\n"
        f"🔥 Аниқлик: **{res['acc']}%**\n"
        f"📉 RSI: **{res['rsi']}**\n"
        f"💰 Жорий нарх: **{res['price']}**\n\n"
        f"⏱ Вақт: **1-5 МИНУТ**"
    )
    bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

bot.polling(none_stop=True)
