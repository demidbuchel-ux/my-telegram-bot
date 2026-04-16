import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Твой токен (уже вставлен)
TOKEN = "8629438921:AAG3d3oeRgRaZtzTotRWr7srd4AlI5CMdsg"

# Настройка логов, чтобы видеть, что происходит
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот Демида. Я работаю на Amvera!")

async def echo(update: Update, context):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

def main():
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд и сообщений
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    print("Бот запущен на Amvera!")
    app.run_polling()

if __name__ == "__main__":
    main()