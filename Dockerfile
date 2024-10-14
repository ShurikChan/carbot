
FROM python:3.12

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY car_api /app/car_api/
COPY TG_BOT /app/TG_BOT/

ENV DJANGO_SETTINGS_MODULE=car_api.settings

# Запуск Django и Telegram бота одновременно
CMD ["sh", "-c", "python car_api/manage.py runserver 0.0.0.0:8000 & python TG_BOT/main.py"]