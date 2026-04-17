import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# --- Импортируем наш «будильник» ---
from keep_alive_ping import create_service

# --- Настройки ---
TOKEN = "8629438921:AAG3d3oeRgRaZtzTotRWr7srd4AlI5CMdsg"

# --- Запускаем «будильник» ---
# Эта строка запускает мини-сервер, который Render будет проверять.
service = create_service()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привет! Я бот Демида и я работаю на Render с будильником!")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")

async def main():
    print(">>> Бот с будильником запущен и слушает Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
