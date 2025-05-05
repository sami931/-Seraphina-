
import telebot
import requests
import yfinance as yf
import openai
import datetime
import os

# ==== CONFIGURATION ====
TELEGRAM_API_KEY = os.environ['TELEGRAM_API_KEY']
NEWS_API_KEY = os.environ['NEWS_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

bot = telebot.TeleBot(TELEGRAM_API_KEY)
user_data = {}

# ==== STYLED SENDER ====
def send_with_style(chat_id, text):
    bot.send_message(chat_id, f"🌸 {text}")

# ==== GPT ADVICE ====
def get_gpt_advice(user_info):
    prompt = f"""
You're Seraphina, a soft-spoken and classy advisor who helps users decide if they should trade futures today. Based on this user's info, give gentle and refined advice.

Capital: {user_info['capital']}
Risk Tolerance: {user_info['risk']}
Experience: {user_info['experience']}
Emotional State: {user_info['emotional_state']}

Respond in a warm, feminine tone with a short recommendation (max 100 words).
"""
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response['choices'][0]['message']['content']

# ==== MARKET NEWS ====
def get_market_news():
    url = f"https://newsapi.org/v2/everything?q=futures%20market&apiKey={NEWS_API_KEY}&pageSize=3&sortBy=publishedAt"
    res = requests.get(url).json()
    articles = res.get('articles', [])
    news = "📰 Here are today's futures market highlights:\n\n"
    for a in articles:
        news += f"• {a['title']} ({a['source']['name']})\n"
    return news

# ==== MARKET SUMMARY ====
def get_market_summary(symbol='ES=F'):
    data = yf.Ticker(symbol)
    hist = data.history(period='1d', interval='5m')
    last = hist.tail(1)
    if last.empty:
        return "Sorry love, I couldn't retrieve the latest data. Try again soon. 🌙"
    price = last['Close'].values[0]
    time = last.index[-1].strftime('%H:%M %p')
    return f"📈 {symbol} futures are trading at ${price:.2f} as of {time}."

# ==== BOT LOGIC ====
@bot.message_handler(commands=['start'])
def greet_user(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'step': 1}
    send_with_style(chat_id, "Hello, darling. I'm Seraphina, your futures trading muse.\nLet's reflect on your readiness.\n\n💬 How much capital are you starting with?")

@bot.message_handler(commands=['news'])
def send_news(message):
    chat_id = message.chat.id
    send_with_style(chat_id, get_market_news())

@bot.message_handler(commands=['summary'])
def send_summary(message):
    chat_id = message.chat.id
    send_with_style(chat_id, get_market_summary())

@bot.message_handler(func=lambda msg: True)
def handle_response(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_data:
        send_with_style(chat_id, "Type /start to begin our conversation, love.")
        return

    step = user_data[chat_id]['step']

    if step == 1:
        user_data[chat_id]['capital'] = text
        user_data[chat_id]['step'] = 2
        send_with_style(chat_id, "Lovely. 💰 What's your risk tolerance? (High, Medium, Low)")

    elif step == 2:
        user_data[chat_id]['risk'] = text
        user_data[chat_id]['step'] = 3
        send_with_style(chat_id, "Got it, sweetheart. 🌷 Have you traded futures before? (Yes/No)")

    elif step == 3:
        user_data[chat_id]['experience'] = text
        user_data[chat_id]['step'] = 4
        send_with_style(chat_id, "And are you feeling emotionally calm and focused today? (Yes/No)")

    elif step == 4:
        user_data[chat_id]['emotional_state'] = text
        advice = get_gpt_advice(user_data[chat_id])
        send_with_style(chat_id, advice)
        user_data.pop(chat_id)

# Start polling
bot.polling()
