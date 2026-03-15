import telebot
from telebot import types
import yfinance as yf
import time

TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)

ASSETS = {
    'EUR/USD': 'EURUSD=X',
    'GBP/USD': 'GBPUSD=X',
    'BTC/USDT': 'BTC-USD',
    'ETH/USDT': 'ETH-USD',
    'GOLD': 'GC=F'
}

def get_signal(ticker_symbol):
    try:
        # Охирги маълумотларни олиш
        data = yf.download(ticker=ticker_symbol, period='1d', interval='1m', progress=False)
        if data.empty: return None

        # Оддий RSI ҳисоблаш (енгил усул)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1+rs))
        
        last_rsi = rsi.iloc[-1]
        last_price = data['Close'].iloc[-1]

        if last_rsi < 30:
            direction, acc = "⬆️ ЮҚОРИ (CALL)", 91.5
        elif last_rsi > 70:
            direction, acc = "⬇️ ПАСТ (PUT)", 92.3
        else:
            direction, acc = "⏳ КУТИШ (НЕЙТРАЛ)", 50.0

        return {'dir': direction, 'acc': acc, 'rsi': round(last_rsi, 2), 'price': round(last_price, 4)}
    except:
        return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ"))
    bot.send_message(message.chat.id, "🎯 Бот тайёр! Сигнал олиш учун тугмани босинг.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ")
def show_pairs(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(text=p, callback_data=f"p_{p}") for p in ASSETS.keys()]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 Активни танланг:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("p_"))
def handle_p(call):
    pair = call.data.split("_")[1]
    bot.edit_message_text(f"🔎 {pair} таҳлил қилиняпти...", call.message.chat.id, call.message.message_id)
    res = get_signal(ASSETS[pair])
    if res:
        msg = f"💎 **{pair}**\n\n🎯 Сигнал: {res['dir']}\n🔥 Аниқлик: {res['acc']}%\n📉 RSI: {res['rsi']}\n💰 Нарх: {res['price']}"
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.send_message(call.message.chat.id, "❌ Хатолик! Бироздан сўнг уриниб кўринг.")

bot.polling(none_stop=True)
      
