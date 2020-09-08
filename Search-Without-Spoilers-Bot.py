import telebot
import time

bot_token = '1350001699:AAGgFC55g8IM8FbQzu4kCbmr1az2aFLXDjo'
bot = telebot.TeleBot(token=bot_token)
print("The bot is now running")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Welcome!')


while True:
    try:
        bot.polling()
    except Exception:
        time.sleep(15)
