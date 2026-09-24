import os
import json
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Отримання токена бота з змінних середовища Railway
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено в змінних середовища!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Посилання на ваш розміщений на GitHub Pages веб-додаток (з версією ?v=100 для оновлення кешу)
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/?v=101"

@dp.message(Command("start"))
async def cmd_start(message: Message):
    # Створюємо кнопку для відкриття міні-додатка (Mini App)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚖 Замовити таксі", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    
    welcome_text = (
        f"Вітаю, {message.from_user.first_name}! 👋\n\n"
        "Це офіційний бот служби таксі в Кобеляках.\n"
        "Натисніть кнопку нижче, щоб відкрити мапу та обрати маршрут:"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)

# Обробка даних, які надсилаються з Web App при натисканні «Замовити таксі»
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get("action") == "new_order":
            address_from = data.get("address_from", "Не вказано")
            address_to = data.get("address_to", "Не вказано")
            
            response_text = (
                "✅ **Ваше замовлення прийнято в роботу!**\n\n"
                f"📍 **Звідки:** {address_from}\n"
                f"🏁 **Куди:** {address_to}\n\n"
                "Очікуйте, пошук вільного автомобіля..."
            )
            
            await message.answer(response_text, parse_mode="Markdown")
            
    except Exception as e:
        logging.error(f"Помилка обробки даних з WebApp: {e}")
        await message.answer("⚠️ Сталася помилка при обробці замовлення. Спробуйте ще раз.")

async def main():
    logging.info("Бот запущено і готовий до роботи...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
