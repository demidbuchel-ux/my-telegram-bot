import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from keep_alive_ping import create_service

# --- Настройки ---
TOKEN = "TOKEN = "8787488197:AAF5pNAmOFwYItzwtVNZWcplXhgxQ1mnBEU"
port = int(os.environ.get("PORT", 10000))
service = create_service(port=port)

logging.basicConfig(level=logging.INFO)

# Хранилище состояний (чтобы помнить, что выбрал пользователь)
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

# Определяем состояния (шаги диалога)
class Form(StatesGroup):
    waiting_for_gender = State()

# --- Клавиатура с выбором пола ---
gender_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👨 Мужчина")],
        [KeyboardButton(text="👩 Женщина")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пол..."
)

# --- Обработчик команды /start ---
@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "Привет! Я бот Демида. Я умею раздевать людей 😏\n\n"
        "Выбери, кого будем раздевать:",
        reply_markup=gender_keyboard
    )
    # Устанавливаем состояние "ожидание выбора пола"
    await state.set_state(Form.waiting_for_gender)

# --- Обработчик выбора пола ---
@dp.message(Form.waiting_for_gender)
async def process_gender(message: types.Message, state: FSMContext):
    user_choice = message.text

    if "Мужчина" in user_choice:
        response = "👔 Вы выбрали мужчину. Снимаем пиджак... галстук... рубашку... Ой, а тут кубики пресса! 🔥"
    elif "Женщина" in user_choice:
        response = "👗 Вы выбрали женщину. Расстёгиваем платье... туфельки... чулочки... Ого, какая красота! 🔥"
    else:
        # Если пользователь написал что-то не то, просим выбрать кнопкой
        await message.answer(
            "Пожалуйста, выберите пол, нажав на одну из кнопок ниже 👇",
            reply_markup=gender_keyboard
        )
        return

    # Отправляем ответ и убираем клавиатуру
    await message.answer(response, reply_markup=ReplyKeyboardRemove())
    # Сбрасываем состояние
    await state.clear()

# --- Обработчик любых других сообщений (если состояние не активно) ---
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("Напиши /start, чтобы начать раздевание 😉")

async def main():
    print(f">>> Бот с раздеванием запущен на порту {port}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
