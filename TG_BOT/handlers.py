import requests
from telebot import types
from utils import register_user, get_user_cars, show_add_car_button
import config

user_data = {}

def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton("Начать")
        markup.add(start_button)

        bot.send_message(chat_id,
                         "Добро пожаловать в бота для автолюбителей! Нажмите кнопку ниже, чтобы приступить к работе.",
                         reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == "Начать")
    def register_or_get_cars(message):
        chat_id = message.chat.id
        username = message.from_user.username

        try:
            response = requests.get(f"{config.API_URL_REG}?username={username}")

            print(f"Проверка пользователя: {username}, Статус код: {response.status_code}")
            if response.status_code == 200:
                users = response.json()
                found_users = [user for user in users if user['username'] == username]

                if found_users:
                    user_id = found_users[0]['id']
                    user_data[chat_id] = {'user_id': user_id, 'username': username}
                    get_user_cars(bot, message, user_id)
                else:
                    register_user(bot, username, chat_id, message)
            else:
                bot.send_message(chat_id, "Ошибка при проверке пользователя.")
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка: {str(e)}")

    @bot.message_handler(func=lambda message: message.text == "Добавить машину")
    def add_car(message):
        chat_id = message.chat.id

        if chat_id in user_data and 'user_id' in user_data[chat_id]:
            user_id = user_data[chat_id]['user_id']
            bot.send_message(chat_id, "Введите марку машины:")
            bot.register_next_step_handler(message, lambda m: get_car_details(bot, m, user_id))
        else:
            bot.send_message(chat_id, "Ошибка: пользователь не найден.")

    def get_car_details(bot, message, user_id):
        # Функция для обработки деталей добавляемой машины
        car_make = message.text
        bot.send_message(message.chat.id, "Введите модель машины:")
        bot.register_next_step_handler(message, lambda m: save_car(bot, m, car_make, user_id))

    def save_car(bot, message, car_make, user_id):
        car_model = message.text
        # Здесь можно добавить логику для сохранения машины через API
        bot.send_message(message.chat.id, f"Машина {car_make} {car_model} успешно добавлена!")

    # Другие обработчики для дополнительных действий...
