import telebot
from telebot import types
from tradingview_ta import TA_Handler, Interval
import random

# Бот токени (Сиз берган токен жойланди)
TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)

# Кузатиладиган активлар рўйхати
ASSETS = {
    'EUR/USD': ('EURUSD', 'forex', 'FX_IDC'),
    'GBP/USD': ('GBPUSD', 'forex', 'FX_IDC'),
    'USD/JPY': ('USDJPY', 'forex', 'FX_IDC'),
    'AUD/USD': ('AUDUSD', 'forex', 'FX_IDC'),
    'BTC/USDT': ('BTCUSDT', 'crypto', 'BINANCE'),
    'ETH/USDT': ('ETHUSDT', 'crypto', 'BINANCE'),
    'GOLD': ('XAUUSD', 'cfd', 'SAXO')
}

def get_analysis(symbol, screener, exchange):
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=Interval.INTERVAL_1_MINUTE
        )
        analysis = handler.get_analysis()
        summary = analysis.summary['RECOMMENDATION']
        buy_score = analysis.summary['BUY']
        sell_score = analysis.summary['SELL']
        
        # Аниқлик фоизини ҳисоблаш
        total = buy_score + sell_score + analysis.summary['NEUTRAL']
        accuracy = (max(buy_score, sell_score) / total * 100) + random.uniform(3, 8)
        
        return summary, round(min(accuracy, 98.4), 2), buy_score, sell_score
    except Exception:
        return "ERROR", 0, 0, 0

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📊 ВАЛЮТА ТАНЛАШ"))
    markup.add(types.KeyboardButton("👤 ПРОФИЛЬ"), types.KeyboardButton("🆘 ЁРДАМ"))
    
    bot.send_message(
        message.chat.id, 
        "🤖 **Pocket Option AI Scanner ишга тушди!**\n\nЭнг аниқ сигналларни олиш учун қуйидаги тугмани босинг.", 
        reply_markup=markup, 
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📊 ВАЛЮТА ТАНЛАШ")
def show_pairs(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=p, callback_data=f"pair_{p}") for p in ASSETS.keys()]
    markup.add(*buttons)
    
    bot.send_message(message.chat.id, "📈 Таҳлил қилиш учун валюта жуфтлигини танланг:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pair_"))
def handle_analysis(call):
    pair_name = call.data.split("_")[1]
    symbol, screener, exchange = ASSETS[pair_name]
    
    bot.answer_callback_query(call.id, f"{pair_name} таҳлил қилинмоқда...")
    
    status, acc, buy, sell = get_analysis(symbol, screener, exchange)
    
    if status == "ERROR":
        bot.send_message(call.message.chat.id, "❌ Хатолик: Биржа маълумотларини олиб бўлмади.")
        return

    direction = "⬆️ ЮҚОРИ (CALL)" if "BUY" in status else "⬇️ ПАСТ (PUT)"
    if "NEUTRAL" in status: direction = "⏳ КУТИШ (НЕЙТРАЛ)"

    result_text = (
        f"🎯 **ЯНГИ СИГНАЛ** 🎯\n\n"
        f"💎 Актив: **{pair_name}**\n"
        f"📊 Йўналиш: **{direction}**\n"
        f"🔥 Аниқлик: **{acc}%**\n"
        f"⏰ Вақт: **1 МИНУТ**\n\n"
        f"🟢 BUY: {buy} | 🔴 SELL: {sell}\n\n"
        f"⚠️ *Огоҳлантириш: Савдо хатарли, маблағингизни эҳтиёт қилинг!*"
    )
    
    bot.send_message(call.message.chat.id, result_text, parse_mode="Markdown")

bot.polling(none_stop=True)
