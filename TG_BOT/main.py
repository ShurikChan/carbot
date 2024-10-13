import telebot
import requests
from telebot import types
import config

bot = telebot.TeleBot(config.BOT_TOKEN)

# Словарь для хранения информации о пользователе
user_data = {}


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

    # Проверяем, есть ли пользователь в базе данных по имени пользователя
    try:
        response = requests.get(f"{config.API_URL_REG}?username={username}")

        print(f"Проверка пользователя: {username}, Статус код: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            found_users = [user for user in users if user['username'] == username]

            if found_users:
                user_id = found_users[0]['id']
                user_data[chat_id] = {'user_id': user_id, 'username': username}
                get_user_cars(message, user_id)
            else:
                # Пользователь не найден, регистрируем нового пользователя
                register_user(username, chat_id, message)
        else:
            bot.send_message(chat_id, "Ошибка при проверке пользователя.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")


def register_user(username, chat_id, message):
    try:
        # Отправляем запрос на регистрацию
        response = requests.post(config.API_URL_REG, json={'username': username, 'password': username})

        if response.status_code == 201:
            user_id = response.json().get('id')
            user_data[chat_id] = {'user_id': user_id, 'username': username}
            bot.send_message(chat_id, "Вы успешно зарегистрированы!")
            get_user_cars(message, user_id)
        else:
            bot.send_message(chat_id, "Произошла ошибка при регистрации.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")


def get_user_cars(message, user_id):
    chat_id = message.chat.id

    # Выполняем запрос на получение машин пользователя
    url = f"{config.API_URL_CARS}?user_id={user_id}"
    print(f"Получение машин для пользователя ID: {user_id}, URL: {url}")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            cars = response.json()
            user_data[chat_id]['cars'] = cars
            if cars:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for car in cars:
                    car_button = types.KeyboardButton(f"{car['make']} {car['model']} ({car['year']})")
                    markup.add(car_button)

                # Добавляем кнопку "Добавить машину" после вывода машин
                add_car_button = types.KeyboardButton("Добавить машину")
                markup.add(add_car_button)
                bot.send_message(chat_id, "Выберите машину:", reply_markup=markup)
            else:
                show_add_car_button(chat_id)
        else:
            bot.send_message(chat_id, "Произошла ошибка при получении списка машин.")
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}")


def show_add_car_button(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_car_button = types.KeyboardButton("Добавить машину")
    markup.add(add_car_button)
    bot.send_message(chat_id, "У вас пока нет машин. Вы можете добавить машину.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Добавить машину")
def add_car(message):
    chat_id = message.chat.id

    if chat_id in user_data and 'user_id' in user_data[chat_id]:
        user_id = user_data[chat_id]['user_id']
        bot.send_message(chat_id, "Введите марку машины:")
        bot.register_next_step_handler(message, lambda m: get_car_details(m, user_id))
    else:
        bot.send_message(chat_id, "Ошибка: пользователь не найден.")


def get_car_details(message, user_id):
    make = message.text
    bot.send_message(message.chat.id, "Введите модель машины:")
    bot.register_next_step_handler(message, lambda m: get_model(m, make, user_id))


def get_model(message, make, user_id):
    model = message.text
    bot.send_message(message.chat.id, "Введите год выпуска (например, 2020):")
    bot.register_next_step_handler(message, lambda m: get_year(m, make, model, user_id))


def get_year(message, make, model, user_id):
    year = message.text
    bot.send_message(message.chat.id, "Введите пробег (например, 50000):")
    bot.register_next_step_handler(message, lambda m: get_mileage(m, make, model, year, user_id))


def get_mileage(message, make, model, year, user_id):
    mileage = message.text
    bot.send_message(message.chat.id, "Введите последнее обслуживание (например, 2023-05-01):")
    bot.register_next_step_handler(message, lambda m: process_last_oil(m, make, model, year, mileage, user_id))


def process_last_oil(message, make, model, year, mileage, user_id):
    last_oil = message.text
    data = {
        "make": make,
        "model": model,
        "year": year,
        "mileage": mileage,
        "last_oil": last_oil,
        "user": user_id
    }

    # Добавляем машину
    response = requests.post(config.API_URL_CARS, json=data)
    print(f"Добавление машины: {response.status_code}, Ответ: {response.json()}")

    if response.status_code == 201:
        bot.send_message(message.chat.id, "Машина успешно добавлена!")
        # Теперь получаем машины для пользователя после добавления
        get_user_cars(message, user_id)
    else:
        bot.send_message(message.chat.id, "Ошибка при добавлении машины.")


@bot.message_handler(func=lambda message: message.text in [f"{car['make']} {car['model']} ({car['year']})" for car in
                                                           user_data.get(message.chat.id, {}).get('cars', [])])
def select_car(message):
    chat_id = message.chat.id
    selected_car = message.text

    # Сохраняем выбранный автомобиль
    if chat_id not in user_data:
        user_data[chat_id] = {}
    user_data[chat_id]['selected_car'] = selected_car  # Сохраняем выбранный автомобиль

    # Извлекаем данные автомобиля из базы данных
    car = get_car_details_from_db(selected_car, chat_id)

    if car:
        # Отправляем данные автомобиля
        bot.send_message(chat_id,
                         f"Выбранный автомобиль:\nМарка: {car['make']}\nМодель: {car['model']}\nГод: {car['year']}\nПробег: {car['mileage']}\nПоследнее обслуживание: {car['last_oil']}")

        # Создаем кнопки для действий
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Замена масла"))
        markup.add(types.KeyboardButton("Сервис"))
        markup.add(types.KeyboardButton("Заметки"))
        markup.add(types.KeyboardButton("Хорошие покупки"))
        markup.add(types.KeyboardButton("Назад"))

        bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Ошибка: автомобиль не найден.")



@bot.message_handler(func=lambda message: message.text == "Назад")
def go_back_to_cars(message):
    chat_id = message.chat.id
    if chat_id in user_data and 'user_id' in user_data[chat_id]:
        user_id = user_data[chat_id]['user_id']
        get_user_cars(message, user_id)
    else:
        bot.send_message(chat_id, "Ошибка: пользователь не найден.")


@bot.message_handler(func=lambda message: message.text == "Замена масла")
def oil_change(message):
    chat_id = message.chat.id

    # Проверяем, есть ли выбранный автомобиль
    if chat_id in user_data and 'selected_car' in user_data[chat_id]:
        selected_car = user_data[chat_id]['selected_car']

        # Получаем информацию о последнем обслуживании
        car = get_car_details_from_db(selected_car, chat_id)

        if car:
            last_oil = car['last_oil']
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Добавить замену масла"))
            markup.add(types.KeyboardButton("История замены масла"))
            markup.add(types.KeyboardButton("Общая сумма"))
            markup.add(types.KeyboardButton("Назад"))

            bot.send_message(chat_id,
                             f"Последняя замена масла для автомобиля {car['make']} {car['model']} была {last_oil}.",
                             reply_markup=markup)
            bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)
        else:
            bot.send_message(chat_id, "Ошибка: выбранный автомобиль не найден.")
    else:
        bot.send_message(chat_id, "Ошибка: выбранный автомобиль не найден.")

def get_car_details_from_db(selected_car, chat_id):
    """Функция для получения деталей автомобиля из базы данных по тексту кнопки"""
    make, model_year = selected_car.rsplit(' ', 1)
    year = model_year.strip('()')
    for car in user_data.get(chat_id, {}).get('cars', []):
        if f"{car['make']} {car['model']} ({car['year']})" == selected_car:
            return car
    return None



# Запускаем бота
bot.polling(none_stop=True)