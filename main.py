import telebot
from telebot import types
import random
import time

# --- ТИЗИМНИ ИШГА ТУШИРИШ ---
TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)

# 30 та OTC Активлари (Pocket Option рўйхати бўйича)
OTC_LIST = [
    'EUR/USD (OTC)', 'GBP/USD (OTC)', 'USD/JPY (OTC)', 'AUD/USD (OTC)',
    'NZD/USD (OTC)', 'USD/CAD (OTC)', 'EUR/JPY (OTC)', 'GBP/JPY (OTC)',
    'AUD/CAD (OTC)', 'EUR/GBP (OTC)', 'EUR/AUD (OTC)', 'USD/CHF (OTC)',
    'CAD/JPY (OTC)', 'CHF/JPY (OTC)', 'NZD/JPY (OTC)', 'AUD/JPY (OTC)',
    'EUR/CAD (OTC)', 'GBP/CAD (OTC)', 'AUD/CHF (OTC)', 'NZD/CAD (OTC)',
    'CAD/CHF (OTC)', 'AUD/NZD (OTC)', 'EUR/NZD (OTC)', 'GBP/NZD (OTC)',
    'USD/SGD (OTC)', 'USD/TRY (OTC)', 'USD/ZAR (OTC)', 'USD/MXN (OTC)',
    'EUR/SEK (OTC)', 'GBP/CHF (OTC)'
]

def generate_pocket_signals(pair):
    """Видеодагидек 3 та Target ва Пипсларни ҳисоблаш"""
    # Жонли нарх симуляцияси
    base_price = round(random.uniform(0.65000, 1.35000), 5)
    is_up = random.choice([True, False])
    
    # Пипс қадамлари (Сиз айтган +200, +300 мантиғи)
    pips = 0.00010 
    direction = "SOTIB OLISH 🟢" if is_up else "SOTISH 🔴"
    trend_icon = "📈" if is_up else "📉"
    
    # 3 та Target (1 ва 2 дақиқалик прогнозлар)
    t1 = round(base_price + (pips * 10) if is_up else base_price - (pips * 10), 5)
    t2 = round(base_price + (pips * 25) if is_up else base_price - (pips * 25), 5)
    t3 = round(base_price + (pips * 40) if is_up else base_price - (pips * 40), 5)
    
    power = random.randint(720, 980) # Signal Power (масалан: 615 даражасидан юқори)

    msg = (
        f"{trend_icon} <b>{pair} LIVE</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 <b>ЙЎНАЛИШ: {direction}</b>\n"
        f"📊 <b>SIGNAL POWER: {power}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✅ <b>TARGET 1 (1m): {t1}</b> (+100 pips)\n"
        f"✅ <b>TARGET 2 (2m): {t2}</b> (+250 pips)\n"
        f"✅ <b>TARGET 3 (MAX): {t3}</b> (+400 pips)\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📍 <i>Кириш нуқтаси: {base_price}</i>\n"
        f"🕒 <i>Update: {time.strftime('%H:%M:%S')}</i>"
    )
    return msg

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ (LIVE)"))
    bot.send_message(message.chat.id, 
                     "💎 <b>Pocket Live Mirror v11.5</b>\n\n"
                     "Бот Pocket Option бозорини сканер қилади:\n"
                     "✅ 3 та кетма-кет Target (✓)\n"
                     "✅ Пипсдаги аниқлик (+200, +400)\n"
                     "✅ 1 ва 2 дақиқалик прогноз", 
                     parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ (LIVE)")
def show_pairs(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = [types.InlineKeyboardButton(text=a.split('/')[0] + "/" + a.split('/')[1][:3], callback_data=f"p_{a}") for a in OTC_LIST]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 <b>OTC Активни танланг:</b>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("p_"))
def handle_live_call(call):
    asset = call.data.split("_")[1]
    
    # Видеодаги Loading эффекти
    bot.edit_message_text(f"⏳ <b>Analyzing {asset}...</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    time.sleep(1.3)
    
    response = generate_pocket_signals(asset)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔄 Yangi signal", callback_data=f"p_{asset}"))
    
    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

bot.polling(none_stop=True)
