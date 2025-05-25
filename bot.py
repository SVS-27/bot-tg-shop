import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import router
import database  # Импортируем файл базы данных

# Загружаем токен
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Ошибка: BOT_TOKEN не найден. Проверьте файл .env!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем обработчики команд
dp.include_router(router)

async def main():
    print("Бот запущен...")
    database  # Это создаст БД, если она еще не существует
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())