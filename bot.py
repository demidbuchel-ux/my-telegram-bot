import os
import asyncio
import logging
import aiohttp
import base64
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from keep_alive_ping import create_service

TELEGRAM_TOKEN = "8787488197:AAF5pNAmOFwYItzwtVNZWcplXhgxQ1mnBEU"
LAB_URL = "https://reforest-eccentric-murky.ngrok-free.dev"  # <-- ОБНОВИ

port = int(os.environ.get("PORT", 10000))
service = create_service(port=port)

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    waiting_for_gender = State()
    waiting_for_photo = State()

gender_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👨 Мужчина")],
        [KeyboardButton(text="👩 Женщина")]
    ],
    resize_keyboard=True
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer("Привет! Выбери пол:", reply_markup=gender_keyboard)
    await state.set_state(Form.waiting_for_gender)

@dp.message(Form.waiting_for_gender)
async def process_gender(message: types.Message, state: FSMContext):
    if message.text not in ["👨 Мужчина", "👩 Женщина"]:
        await message.answer("Выбери кнопкой 👇", reply_markup=gender_keyboard)
        return
    await state.update_data(gender=message.text)
    await message.answer("Отправь фото:", reply_markup=cancel_keyboard)
    await state.set_state(Form.waiting_for_photo)

@dp.message(Form.waiting_for_photo, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    wait_msg = await message.answer("🔄 Отправляю в лабораторию... Жди 1-2 минуты.")

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file.file_path}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{LAB_URL}/process",
                json={"image_url": file_url, "gender": (await state.get_data()).get("gender")},
                timeout=aiohttp.ClientTimeout(total=600)
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("status") == "success":
                        img_bytes = base64.b64decode(result["image_base64"])
                        # Отправляем как файл (правильный способ для aiogram 3.x)
                        await message.answer_photo(
                            BufferedInputFile(img_bytes, filename="result.png"),
                            caption="✨ Готово! Наслаждайся."
                        )
                    else:
                        await message.answer(f"😕 Ошибка: {result.get('message')}")
                else:
                    await message.answer(f"😕 Ошибка лаборатории: {resp.status}")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer(f"😕 Ошибка связи: {e}")

    await wait_msg.delete()
    await message.answer("Возвращаю в меню.", reply_markup=gender_keyboard)
    await state.clear()

@dp.message(Form.waiting_for_photo, F.text == "❌ Отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=gender_keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
