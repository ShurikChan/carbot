import telebot
from telebot import types
import requests

BOT_TOKEN = '7043798224:AAHZrDLpywajeS6TzJZdr767Lba9CHabHko'
API_URL_REG = 'http://localhost:8000/register_user/'
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text="Register", callback_data="register")
    keyboard.add(button)
    bot.reply_to(message, "Howdy, how are you doing?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "register")
def register_user(call):
    user_id = call.from_user.id
    data = {"username": user_id, "password": user_id}  # Имя = Паролю
    requests.post(API_URL_REG, json=data)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id, text="Аккаунт создан")


if __name__ == '__main__':
    bot.polling()
