import requests
from telebot import types
import config

def register_user(bot, username, chat_id, message):
    try:
        response = requests.post(config.API_URL_REG, json={'username': username, 'password': username})

        if response.status_code == 201:
            user_id = response.json().get('id')
            bot.send_message(chat_id, "Вы успешно зарегистрированы!")
            get_user_cars(bot, message, user_id)
        else:
            bot.send_message(chat_id, "Произошла ошибка при регистрации.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")

def get_user_cars(bot, message, user_id):
    chat_id = message.chat.id
    url = f"{config.API_URL_CARS}?user_id={user_id}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            cars = response.json()
            if cars:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for car in cars:
                    car_button = types.KeyboardButton(f"{car['make']} {car['model']} ({car['year']})")
                    markup.add(car_button)
                add_car_button = types.KeyboardButton("Добавить машину")
                markup.add(add_car_button)
                bot.send_message(chat_id, "Выберите машину:", reply_markup=markup)
            else:
                show_add_car_button(bot, chat_id)
        else:
            bot.send_message(chat_id, "Произошла ошибка при получении списка машин.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")

def show_add_car_button(bot, chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_car_button = types.KeyboardButton("Добавить машину")
    markup.add(add_car_button)
    bot.send_message(chat_id, "У вас пока нет машин. Вы можете добавить машину.", reply_markup=markup)

# Дополнительные вспомогательные функции...
