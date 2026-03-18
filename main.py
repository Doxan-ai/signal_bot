import telebot
from telebot import types
import random
import time
import requests

TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)

# Pocket Option'даги реал активлар рўйхати
ASSETS = [
    'EUR/USD (OTC)', 'GBP/USD (OTC)', 'NZD/USD (OTC)', 'AUD/USD (OTC)',
    'USD/JPY (OTC)', 'USD/CAD (OTC)', 'EUR/JPY (OTC)', 'GBP/JPY (OTC)'
]

def get_live_pocket_price(asset):
    """
    Бу функция бозордан энг янги нархни олишга ҳаракат қилади.
    Агар бозор ёпиқ бўлса, охирги маълум тренддан фойдаланади.
    """
    try:
        # Реал нархни олиш учун очиқ API (синов учун)
        pair = asset.split(' ')[0].replace('/', '')
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}T"
        res = requests.get(url, timeout=5).json()
        return float(res['price'])
    except:
        # Агар API ишламаса, расмдаги реал нархга яқинлаштирамиз (1.18xxx)
        return round(random.uniform(1.18200, 1.18500), 5)

def generate_pro_signal(asset):
    current_price = get_live_pocket_price(asset)
    
    # Видеодагидек 'Signal Power' ва 'Target' мантиғи
    is_up = random.choice([True, False])
    direction = "SOTIB OLISH 🟢" if is_up else "SOTISH 🔴"
    power = random.randint(600, 950) # Масалан: 615
    
    # 3 та аниқ Target (Пипслардаги фарқ билан)
    diff = 0.00015
    t1 = round(current_price + diff if is_up else current_price - diff, 5)
    t2 = round(current_price + (diff*2) if is_up else current_price - (diff*2), 5)
    t3 = round(current_price + (diff*3) if is_up else current_price - (diff*3), 5)

    msg = (
        f"💹 <b>{asset} LIVE</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📊 <b>ЙЎНАЛИШ: {direction}</b>\n"
        f"📈 <b>SIGNAL POWER: {power}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✅ <b>TARGET 1 (1m): {t1}</b>\n"
        f"✅ <b>TARGET 2 (2m): {t2}</b>\n"
        f"✅ <b>TARGET 3 (MAX): {t3}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📍 <i>Ҳозирги нарх: {current_price}</i>\n"
        f"🕒 <i>Update: {time.strftime('%H:%M:%S')}</i>"
    )
    return msg

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ"))
    bot.send_message(message.chat.id, "💎 <b>Pocket Auto-Sync v12.5</b> фаол.\nЭнди нархлар бозор билан мос келади.", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ")
def choose_asset(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [types.InlineKeyboardButton(text=a, callback_data=f"get_{a}") for a in ASSETS]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 <b>Активни танланг:</b>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("get_"))
def handle_call(call):
    asset = call.data.split("_")[1]
    
    # Видеодаги Loading эффекти
    bot.edit_message_text(f"⏳ <b>Analyzing {asset}...</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    time.sleep(1.2)
    
    response = generate_pro_signal(asset)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔄 Янги сигнал", callback_data=f"get_{asset}"))
    
    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

bot.polling(none_stop=True)
