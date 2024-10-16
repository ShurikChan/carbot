import telebot
import requests
from telebot import types
import config
from datetime import datetime

bot = telebot.TeleBot(config.BOT_TOKEN)

# Словарь для хранения информации о пользователе
user_data = {}

# Приветсвеное сообщение
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton("Начать")
    markup.add(start_button)

    bot.send_message(chat_id,
                     "Добро пожаловать в бота для автолюбителей! Нажмите кнопку ниже, чтобы приступить к работе.",
                     reply_markup=markup)

# Кнопка начать и проверка пользователя
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

# Регистрация пользователя
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
    bot.send_message(message.chat.id, "Введите замену масла (например, 50000):")
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

@bot.message_handler(func=lambda message: message.text == "Добавить замену масла")
def prompt_oil_change(message):
    chat_id = message.chat.id

    if chat_id in user_data and 'selected_car' in user_data[chat_id]:
        selected_car = user_data[chat_id]['selected_car']
        car = get_car_details_from_db(selected_car, chat_id)

        if car:
            bot.send_message(chat_id, "Введите пробег сейчас:")
            bot.register_next_step_handler(message, lambda m: get_mileage_oil(m, car))
        else:
            bot.send_message(chat_id, "Ошибка: выбранный автомобиль не найден.")
    else:
        bot.send_message(chat_id, "Ошибка: выбранный автомобиль не найден.")

def get_mileage_oil(message, car):
    mileage_oil = message.text
    bot.send_message(message.chat.id, "Введите цену замены масла:")
    bot.register_next_step_handler(message, lambda m: get_price_oil(m, car, mileage_oil))

def get_price_oil(message, car, mileage_oil):
    price = message.text
    bot.send_message(message.chat.id, "Введите название масла:")
    bot.register_next_step_handler(message, lambda m: get_name_oil(m, car, mileage_oil, price))

def get_name_oil(message, car, mileage_oil, price):
    name_oil = message.text
    bot.send_message(message.chat.id, "Введите следующую замену масла (пробег):")
    bot.register_next_step_handler(message, lambda m: finalize_oil_change(m, car, mileage_oil, price, name_oil))

def finalize_oil_change(message, car, mileage_oil, price, name_oil):
    next_mileage_oil = message.text
    bot_data = {
        'car_id': car['id'],
        'millage_oil': mileage_oil,
        'next_millage_oil': next_mileage_oil,
        'price': price,
        'name_oil': name_oil
    }

    # Запрашиваем изображение у пользователя
    bot.send_message(message.chat.id, "Загрузите изображение квитанции или пропустите, отправив 'Нет'.")
    bot.register_next_step_handler(message, process_oil_change_image, bot_data)


# Шаг 2: Обработка изображения или пропуска
def process_oil_change_image(message, bot_data):
    url = 'http://127.0.0.1:8000/oil-service/'

    # Проверяем, отправил ли пользователь изображение
    if message.content_type == 'photo':
        # Получаем файл изображения
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_extension = file_info.file_path.split('.')[-1]
        filename = f"oil_receipt.{file_extension}"
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)
        with open(filename, 'rb') as image_file:
            files = {'image': (filename, image_file, f"image/{file_extension}")}
            data = {
                'car': bot_data['car_id'],
                'millage_oil': bot_data['millage_oil'],
                'next_millage_oil': bot_data['next_millage_oil'],
                'price': bot_data['price'],
                'name_oil': bot_data['name_oil']
            }
            try:
                response = requests.post(url, data=data, files=files)
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")

                if response.status_code == 200:
                    bot.send_message(message.chat.id, "Замена масла успешно добавлена!")
                else:
                    print(f"Ошибка: {response.status_code}. Ответ: {response.text}")
            except requests.exceptions.RequestException as e:
                bot.send_message(message.chat.id, f"Ошибка при отправке данных: {e}")
    elif message.text.lower() == 'нет':
        data = {
            'car': bot_data['car_id'],
            'millage_oil': bot_data['millage_oil'],
            'next_millage_oil': bot_data['next_millage_oil'],
            'price': bot_data['price'],
            'name_oil': bot_data['name_oil']
        }
        try:
            response = requests.post(url, json=data)
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")

            if response.status_code == 201:
                bot.send_message(message.chat.id, "Замена масла успешно добавлена без изображения!")
            else:
                print(f"Ошибка: {response.status_code}. Ответ: {response.text}")
        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f"Ошибка при отправке данных: {e}")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, загрузите изображение или введите 'Нет'.")



@bot.message_handler(func=lambda message: message.text == "История замены масла")
def show_oil_change_history(message):
    chat_id = message.chat.id

    # Проверяем, есть ли выбранный автомобиль
    if chat_id in user_data and 'selected_car' in user_data[chat_id]:
        selected_car = user_data[chat_id]['selected_car']

        # Извлекаем данные автомобиля
        car = get_car_details_from_db(selected_car, chat_id)

        if car:
            car_id = car['id']
            # Делаем запрос на сервер для получения истории замен масла
            try:
                response = requests.get(f"{config.API_URL_OIL}?car_id={car_id}")
                if response.status_code == 200:
                    oil_changes = response.json()
                    if oil_changes:
                        # Формируем сообщение с историей замен
                        history_message = "История замены масла:\n\n"
                        for oil_change in oil_changes:
                            # Преобразование даты с учетом миллисекунд
                            date_object = datetime.strptime(oil_change['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                            formatted_date = date_object.strftime('%Y-%m-%d')

                            history_message += (
                                f"Дата: {formatted_date}\n"  # Отформатированная дата
                                f"Пробег: {oil_change['millage_oil']}\n"
                                f"Название масла: {oil_change['name_oil']}\n"
                                f"Цена: {oil_change['price']} руб.\n"
                                f"Следующая замена: {oil_change['next_millage_oil']}\n"
                                f"Фото: {oil_change['image'] if oil_change['image'] else 'Не загружено'}\n\n"
                            )
                        bot.send_message(chat_id, history_message)
                    else:
                        bot.send_message(chat_id, "История замен масла отсутствует.")
                else:
                    bot.send_message(chat_id, "Ошибка при получении истории замен масла.")
            except Exception as e:
                bot.send_message(chat_id, f"Ошибка: {str(e)}")
        else:
            bot.send_message(chat_id, "Ошибка: выбранный автомобиль не найден.")
    else:
        bot.send_message(chat_id, "Ошибка: выбранный автомобиль не найден.")

@bot.message_handler(func=lambda message: message.text == "Общая сумма")
def get_total_oil_expense(message):
    chat_id = message.chat.id

    # Проверяем, выбран ли автомобиль
    if chat_id in user_data and 'selected_car' in user_data[chat_id]:
        selected_car = user_data[chat_id]['selected_car']

        # Получаем данные автомобиля (например, ID) для выполнения запроса
        car = get_car_details_from_db(selected_car, chat_id)

        if car:
            # Делаем запрос на сервер для получения истории замен масла для автомобиля
            url = f"{config.API_URL_OIL}?car_id={car['id']}"
            response = requests.get(url)

            if response.status_code == 200:
                oil_services = response.json()

                # Суммируем затраты на замену масла
                total_expense = sum(float(service['price']) for service in oil_services)

                bot.send_message(chat_id, f"Общая сумма затрат на замену масла: {total_expense:.2f} руб.")
            else:
                bot.send_message(chat_id, "Произошла ошибка при получении данных о замене масла.")
        else:
            bot.send_message(chat_id, "Ошибка: выбранный автомобиль не найден.")
    else:
        bot.send_message(chat_id, "Ошибка: выбранный автомобиль не найден.")

def get_car_details_from_db(selected_car, chat_id):
    make, model_year = selected_car.rsplit(' ', 1)
    year = model_year.strip('()')
    for car in user_data.get(chat_id, {}).get('cars', []):
        if f"{car['make']} {car['model']} ({car['year']})" == selected_car:
            return car
    return None



# Запускаем бота
bot.polling(none_stop=True)