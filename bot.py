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
LAB_URL = "https://reforest-eccentric-murky.ngrok-free.dev"  # замени на актуальный!

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
    resize_keyboard=True,
    input_field_placeholder="Выбери пол..."
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отмена")]],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Привет! Я бот Демида. 👋\n\nВыбери, кого будем раздевать:",
        reply_markup=gender_keyboard
    )
    await state.set_state(Form.waiting_for_gender)

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

@dp.message(Form.waiting_for_photo, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    wait_msg = await message.answer("🔄 Получил фото! Отправляю в лабораторию... Жди до 2 минут.")

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
                response_text = await resp.text()
                logging.info(f"Ответ лаборатории: статус {resp.status}, тело: {response_text[:200]}")

                if resp.status == 200:
                    try:
                        result = json.loads(response_text)
                        if result.get("status") == "success":
                            img_data = base64.b64decode(result["image_base64"])
                            # Исправление здесь: оборачиваем байты в BufferedInputFile
                            photo_file = BufferedInputFile(img_data, filename="result.png")
                            await message.answer_photo(photo_file, caption="✨ Готово! Наслаждайся.")
                        else:
                            await message.answer(f"😕 Ошибка лаборатории: {result.get('message')}")
                    except Exception as e:
                        await message.answer(f"😕 Ошибка при чтении ответа: {e}")
                else:
                    await message.answer(f"😕 Ошибка лаборатории: {resp.status}\n{response_text[:200]}")
    except asyncio.TimeoutError:
        await message.answer("😕 Лаборатория думала слишком долго. Попробуй другое фото.")
    except aiohttp.ClientConnectorError:
        await message.answer("😕 Не удалось подключиться к лаборатории. Проверь, что Colab запущен и туннель активен.")
    except Exception as e:
        logging.error(f"Ошибка связи с лабораторией: {e}")
        await message.answer(f"😕 Неизвестная ошибка: {e}")

    await wait_msg.delete()
    await message.answer("Возвращаю в главное меню.", reply_markup=gender_keyboard)
    await state.clear()

@dp.message(Form.waiting_for_photo, F.text == "❌ Отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=gender_keyboard)

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("Используй /start, чтобы начать.")

async def main():
    print(f">>> Бот запущен на порту {port}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
