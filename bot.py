import os
import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from keep_alive_ping import create_service

# ================= НАСТРОЙКИ =================
TELEGRAM_TOKEN = "8787488197:AAF5pNAmOFwYItzwtVNZWcplXhgxQ1mnBEU"
# Твоя действующая ссылка на лабораторию Colab
LAB_URL = "https://reforest-eccentric-murky.ngrok-free.dev"
# ============================================

# Будильник для Render
port = int(os.environ.get("PORT", 10000))
service = create_service(port=port)

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=storage)

# Состояния
class Form(StatesGroup):
    waiting_for_gender = State()
    waiting_for_photo = State()

# Клавиатуры
gender_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👨 Мужчина")],
        [KeyboardButton(text="👩 Женщина")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери пол..."
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

# /start
@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Привет! Я бот Демида. 👋\n\n"
        "Выбери, кого будем раздевать:",
        reply_markup=gender_keyboard
    )
    await state.set_state(Form.waiting_for_gender)

# Выбор пола
@dp.message(Form.waiting_for_gender)
async def process_gender(message: types.Message, state: FSMContext):
    choice = message.text
    if choice not in ["👨 Мужчина", "👩 Женщина"]:
        await message.answer("Пожалуйста, выбери пол кнопкой 👇", reply_markup=gender_keyboard)
        return

    await state.update_data(gender=choice)
    await message.answer(
        f"Отлично! Ты выбрал {choice}. Теперь отправь мне фотографию.",
        reply_markup=cancel_keyboard
    )
    await state.set_state(Form.waiting_for_photo)

# Обработка фото
@dp.message(Form.waiting_for_photo, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    wait_msg = await message.answer("🔄 Получил фото! Отправляю в лабораторию... Подожди немного.")

    # Получаем файл фото
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path}"

    # Отправляем в Colab
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{LAB_URL}/process",
                json={"image_url": file_url, "gender": (await state.get_data()).get("gender")},
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    await message.answer(f"✅ Лаборатория ответила: {result.get('message', 'OK')}")
                else:
                    await message.answer(f"😕 Ошибка лаборатории: {resp.status}")
        except Exception as e:
            logging.error(f"Ошибка связи с лабораторией: {e}")
            await message.answer("😕 Не удалось связаться с лабораторией. Попробуй позже.")

    await wait_msg.delete()
    await message.answer("Возвращаю в главное меню.", reply_markup=gender_keyboard)
    await state.clear()

# Отмена
@dp.message(Form.waiting_for_photo, F.text == "❌ Отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=gender_keyboard)

# Прочие сообщения
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("Используй /start, чтобы начать.")

async def main():
    print(f">>> Бот с лабораторией запущен на порту {port}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
