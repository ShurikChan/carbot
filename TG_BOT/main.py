import telebot
from telebot import types
import requests
from config import *


bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


@bot.callback_query_handler(func=lambda call: call.data == "add_car")
def add_car(call):
    bot.send_message(call.message.chat.id, "Введите марку машины:")
    bot.register_next_step_handler(call.message, get_make)


def get_make(message):
    make = message.text
    bot.send_message(message.chat.id, "Введите модель машины:")
    bot.register_next_step_handler(message, get_model, make)


def get_model(message, make):
    model = message.text
    bot.send_message(message.chat.id, "Введите год выпуска машины:")
    bot.register_next_step_handler(message, get_year, make, model)


def get_year(message, make, model):
    mileage = message.text
    bot.send_message(message.chat.id, "Введите примерный пробег машины:")
    bot.register_next_step_handler(message, get_mileage, make, model, mileage)


def get_mileage(message, make, model, year):
    mileage = message.text
    data = {
        "user": message.from_user.id,
        "make": make,
        "model": model,
        "year": year,
        "mileage": mileage
    }

    response = requests.post(API_URL_CARS, json=data)
    if response.status_code == 201:
        bot.send_message(message.chat.id, "Машина успешно добавлена!")
    else:
        bot.send_message(
            message.chat.id, "Произошла ошибка при добавлении машины.")


def add_car_button(message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text="+", callback_data="add_car")
    keyboard.add(button)
    return bot.send_message(message.chat.id, text="Добавить авто",
                            reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text="Начать работу", callback_data="register")
    keyboard.add(button)
    bot.reply_to(message, "Добро пожаловать в бота для автолюбителей, нажмите кнопку ниже, чтобы приступить к работе",
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
                              message_id=call.message.message_id, text="Доступные команды - /cars")
    else:
        data = {"username": user_id, "password": user_id}  # Имя = Паролю
        requests.post(API_URL_REG, json=data)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text="Доступные команды - /cars")


@bot.message_handler(commands=['cars'])
def get_cars(message):
    user_id = message.from_user.id
    keyboard = types.InlineKeyboardMarkup()
    response = requests.get(API_URL_CARS)
    cars = response.json()
    filtered_cars = filter(
        lambda user: user['user'] == str(user_id), cars)
    found_cars = list(filtered_cars)
    if found_cars:
        for car in found_cars:
            button = types.InlineKeyboardButton(
                text=f"{car['make']} {car['model']} ({car['year']})", callback_data=str(car['id']))
            keyboard.add(button)
        bot.send_message(message.chat.id, f"Выберите машину: ",
                         reply_markup=keyboard)
        add_car_button(message)
    else:
        bot.send_message(message.chat.id, text="Автомобилей пока нет")
        add_car_button(message)


if __name__ == '__main__':
    bot.polling(none_stop=True)
