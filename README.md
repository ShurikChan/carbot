# Car_enthusiasts_bot

Это бот для Telegram, который помогает пользователям получать информацию о машинах и автомобильных событиях.

## Установка и запуск

1. Установите Docker на ваш сервер.

2. Скачайте исходный код проекта:

```bash
git clone https://github.com/your_username/Car_enthusiasts_bot.git
cd Car_enthusiasts_bot

3.
Создайте файл .env и добавьте в него необходимые переменные окружения:
TELEGRAM_TOKEN=your_telegram_bot_token

4.
Создайте Docker образ и контейнер:
docker build -t car_enthusiasts_bot .
docker run -d --name car_enthusiasts_bot -v $(pwd):/app --env-file .env car_enthusiasts_bot

5.
Ваш бот теперь должен быть запущен и готов к работе.

6. Чтобы остановить работу бота :
docker stop car_enthusiasts_bot