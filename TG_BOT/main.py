import telebot
from telebot import types
import requests
from config import *


bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text="Register", callback_data="register")
    keyboard.add(button)
    bot.reply_to(message, "Howdy, how are you doing?",
                 reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "register")
def register_user(call):
    user_id = call.from_user.id
    response = requests.get(API_URL_REG)
    users = response.json()
    filtered_users = filter(
        lambda user: user['username'] == str(user_id), users)
    found_users = list(filtered_users)
    if found_users:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Такой пользователь уже зарегистрирован")
    else:
        data = {"username": user_id, "password": user_id}  # Имя = Паролю
        requests.post(API_URL_REG, json=data)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Аккаунт создан")


@bot.message_handler(commands=['cars'])
def get_cars(message):
    user_id = message.from_user.id
    keyboard = types.InlineKeyboardMarkup()
    response = requests.get(API_URL_CARS)
    cars = response.json()
    filtered_cars = filter(
        lambda user: user['user']['username'] == str(user_id), cars)
    found_cars = list(filtered_cars)
    for car in found_cars:
        button = types.InlineKeyboardButton(
            text=f"{car['make']} {car['model']} ({car['year']})", callback_data=str(car['id']))
        keyboard.add(button)
    bot.send_message(message.chat.id, f"Выберите машину: ",
                     reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True)
