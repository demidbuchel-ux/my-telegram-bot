import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменной окружения Render
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден! Укажите BOT_TOKEN в переменных окружения.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! Я бот Демида и я работаю на Render!")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")

async def main():
    print("Бот запущен и слушает...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
