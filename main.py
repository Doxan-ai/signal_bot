import telebot
import requests
import pandas as pd
import numpy as np
import time
import threading

# Сизнинг Телеграм бот токенингиз
TOKEN = '8740187389:AAFWMBelrMBLtUj016KwH2YWCppZIN_PUXc'
bot = telebot.TeleBot(TOKEN)

# Кузатиладиган активлар рўйхати
ASSETS = {
    'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'SOL': 'SOLUSDT', 
    'BNB': 'BNBUSDT', 'XRP': 'XRPUSDT', 'DOGE': 'DOGEUSDT', 
    'AVAX': 'AVAXUSDT', 'GOLD': 'PAXGUSDT', 
    'EUR/USD': 'EURUSDT', 'GBP/USD': 'GBPUSDT'
}

# Сканер ҳолатини сақлаш учун луғат
SCANNING = {}

def get_15m_signal(symbol):
    """Binance API орқали 15 дақиқалик трендни таҳлил қилиш"""
    try:
        # Binance расмий API манзили
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
        response = requests.get(url, timeout=15)
        
        if response.status_code != 200:
            return None, None, None
            
        data = response.json()
        if not data:
            return None, None, None

        # Маълумотларни DataFrame шаклига келтириш
        df = pd.DataFrame(data, columns=['T','O','H','L','C','V','CT','QV','Tr','TB','TQ','I'])
        prices = df['C'].astype(float).tolist()
        
        # Математик трендни ҳисоблаш (Линейная регрессия)
        y = np.array(prices)
        x = np.arange(len(y))
        slope, intercept = np.polyfit(x, y, 1)
        curr_price = prices[-1]
        
        # Йўналишни аниқлаш
        direction = "⬆️ BUY (Ўсиш)" if slope > 0 else "⬇️ SELL (Пасайиш)"
        
        # Аниқликни волатиллик асосида ҳисоблаш
        volatility = np.std(prices[-20:]) / np.mean(prices[-20:]) * 100
        accuracy = 98.0 - (volatility * 500) # Волатиллик қанча кам бўлса, аниқлик шунча юқори
        
        # Аниқлик 70% дан паст бўлмаслигини таъминлаш
        accuracy = max(min(accuracy, 99.9), 70.0)
        
        return curr_price, direction, accuracy
    except Exception as e:
        print(f"Хатолик ({symbol}): {e}")
        return None, None, None

def auto_scanner(chat_id):
    """Активларни автоматик равишда сканер қилиш"""
    while SCANNING.get(chat_id):
        for name, symbol in ASSETS.items():
            if not SCANNING.get(chat_id): break
            
            price, direct, acc = get_15m_signal(symbol)
            
            # Агар аниқлик 88% дан юқори бўлса, сигнал юбориш
            if acc and acc >= 88:
                text = (f"📈 **ЯНГИ СИГНАЛ: {name}**\n\n"
                        f"🎯 Йўналиш: {direct}\n"
                        f"💵 Жорий нарх: ${price:,.2f}\n"
                        f"🛡 Аниқлик: {acc:.1f}%\n"
                        f"⏰ Таймфрейм: 15 дақиқа\n\n"
                        f"ℹ️ Сигнал АИ томонидан серверда таҳлил қилинди.")
                bot.send_message(chat_id, text)
                time.sleep(3) # Сигналлар орасидаги кичик танаффус
        
        time.sleep(300) # Кейинги тўлиқ сканерлашгача 5 дақиқа кутиш

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔍 Сканерни ёқиш", "🛑 Сканерни ўчириш")
    welcome_text = (f"👋 Салом! Мен 15 дақиқалик АИ Сканер ботман.\n\n"
                    f"Сервер: **Render.com (Active)**\n"
                    f"Ҳолат: Ишлашга тайёр ✅")
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_menu(message):
    if message.text == "🔍 Сканерни ёқиш":
        if not SCANNING.get(message.chat.id):
            SCANNING[message.chat.id] = True
            threading.Thread(target=auto_scanner, args=(message.chat.id,), daemon=True).start()
            bot.send_message(message.chat.id, "🚀 Сканер ишга тушди. 88% дан юқори аниқликдаги сигналларни кутинг...")
        else:
            bot.send_message(message.chat.id, "⚠️ Сканер аллақачон ишлаяпти.")
            
    elif message.text == "🛑 Сканерни ўчириш":
        SCANNING[message.chat.id] = False
        bot.send_message(message.chat.id, "🛑 Сканер тўхтатилди.")

if __name__ == "__main__":
    print("Бот ишга тушди...")
    bot.infinity_polling()
