import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Читаем токен из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверяем, загружен ли токен
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Проверьте файл .env")
