import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Твой токен (уже вставлен)
TOKEN = "8629438921:AAG3d3oeRgRaZtzTotRWr7srd4AlI5CMdsg"

# Порт для веб-сервера (прописан жестко)
PORT = 10000

# Создаём бота и диспетчер
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ===== Обработчики команд Telegram =====
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("ВАМ ОДОБРЕН КРЕДИТ")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")

# ===== Маленький веб-сервер для health check =====
async def handle_health(request):
    return web.Response(text="OK")

async def run_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Веб-сервер запущен на порту {PORT}")

# ===== Главная функция =====
async def main():
    # Запускаем веб-сервер
    await run_web_server()
    # Запускаем бота
    logging.info("Бот запущен и слушает Telegram...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
