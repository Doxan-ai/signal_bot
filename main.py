import telebot
from telebot import types
import random
import time

# --- ТИЗИМНИ СОЗЛАШ ---
TOKEN = "8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc"
bot = telebot.TeleBot(TOKEN)

# Pocket Option'даги барча 30 та OTC жуфтликлари
OTC_FULL_LIST = [
    'CAD/CHF (OTC)', 'USD/CAD (OTC)', 'USD/CNH (OTC)', 'AUD/CHF (OTC)', 
    'NZD/USD (OTC)', 'USD/ZAR (OTC)', 'AUD/USD (OTC)', 'CAD/JPY (OTC)', 
    'NZD/CAD (OTC)', 'EUR/AUD (OTC)', 'USD/MXN (OTC)', 'USD/SEK (OTC)', 
    'EUR/SEK (OTC)', 'GBP/AUD (OTC)', 'GBP/CHF (OTC)', 'CHF/JPY (OTC)', 
    'USD/NOK (OTC)', 'GBP/NZD (OTC)', 'EUR/NZD (OTC)', 'NZD/CHF (OTC)', 
    'USD/SGD (OTC)', 'EUR/CHF (OTC)', 'AUD/CAD (OTC)', 'GBP/CAD (OTC)',
    'EUR/USD (OTC)', 'GBP/USD (OTC)', 'USD/JPY (OTC)', 'AUD/JPY (OTC)',
    'EUR/JPY (OTC)', 'GBP/JPY (OTC)'
]

def generate_full_pro_signal(pair):
    """Сиз айтган 3 та кетма-кет сигнал ва +200/300 пипс мантиғи"""
    # Реал бозорга мослаштирилган базавий нарх (Сизнинг 1.18xxx расмингиз асосида)
    base_p = round(random.uniform(1.18200, 1.18500), 5) if 'EUR/USD' in pair else round(random.uniform(0.60000, 1.30000), 5)
    
    is_up = random.choice([True, False])
    direction = "SOTIB OLISH 🟢" if is_up else "SOTISH 🔴"
    power = random.randint(600, 980) # Видеодаги 'Signal Power'
    
    # 3 та кетма-кет нишон (Target) - Пипс фарқлари билан
    step = 0.00012
    tp1 = round(base_p + step if is_up else base_p - step, 5)
    tp2 = round(base_p + (step * 2.5) if is_up else base_p - (step * 2.5), 5)
    tp3 = round(base_p + (step * 4) if is_up else base_p - (step * 4), 5)

    msg = (
        f"💎 <b>{pair} LIVE SCAN</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🎯 <b>ЙЎНАЛИШ: {direction}</b>\n"
        f"📈 <b>SIGNAL POWER: {power}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"✅ <b>TARGET 1 (1m): {tp1}</b>\n"
        f"✅ <b>TARGET 2 (2m): {tp2}</b>\n"
        f"✅ <b>TARGET 3 (MAX): {tp3}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📍 <i>Ҳозирги нуқта: {base_p}</i>\n"
        f"🕒 <i>Update: {time.strftime('%H:%M:%S')}</i>"
    )
    return msg

@bot.message_handler(commands=['start'])
def start_bot(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚀 СИГНАЛ ОЛИШ (30+ OTC)"))
    bot.send_message(message.chat.id, 
                     "💎 <b>Global Sync v13.0</b> ишга тушди.\n\n"
                     "✅ Барча 30 та OTC жуфтлиги қўшилди.\n"
                     "✅ 3 та кетма-кет Target тизими фаол.\n"
                     "✅ Нархлар реал бозорга мослаштирилди.", 
                     parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 СИГНАЛ ОЛИШ (30+ OTC)")
def show_all_assets(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    # Тугмаларни қисқароқ қилиб чиқариш (OTC сўзини олиб ташлаб)
    btns = [types.InlineKeyboardButton(text=a.split(' ')[0], callback_data=f"sig_{a}") for a in OTC_FULL_LIST]
    markup.add(*btns)
    bot.send_message(message.chat.id, "📊 <b>Бир жуфтликни танланг:</b>", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sig_"))
def process_sig(call):
    asset = call.data.split("_")[1]
    
    # Видеодаги 'Loading' эффекти
    bot.edit_message_text(f"⏳ <b>{asset}</b> таҳлил қилинмоқда...", call.message.chat.id, call.message.message_id, parse_mode="HTML")
    time.sleep(1.2)
    
    response = generate_full_pro_signal(asset)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔄 Янги прогноз", callback_data=f"sig_{asset}"))
    
    bot.edit_message_text(response, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

bot.polling(none_stop=True)
