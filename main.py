import os
import json
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DRIVER_CHAT_ID = os.getenv("DRIVER_CHAT_ID") # Наприклад: "-1001234567890"

if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Вставте тут актуальне посилання на ваш сайт із GitHub Pages
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/?v=106"

@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚖 Замовити таксі (Карта)", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    
    welcome_text = (
        f"Вітаю, {message.from_user.first_name}! 👋\n\n"
        "Це офіційний бот служби таксі в Кобеляках.\n"
        "Натисніть кнопку нижче, щоб відкрити карту та оформити замовлення:"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)

# Надійний обробник даних від WebApp
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        # Розшифровуємо JSON, який надіслав сайт
        data = json.loads(message.web_app_data.data)
        
        address_from = data.get("address_from", "Не вказано")
        address_to = data.get("address_to", "Не вказано")
        user_name = message.from_user.first_name
        user_id = message.from_user.id
        
        # 1. Відправляємо підтвердження клієнту в особисті повідомлення
        client_text = (
            "✅ **Ваше замовлення прийнято в роботу!**\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n\n"
            "⏳ Очікуйте, шукаємо вільне авто..."
        )
        await message.answer(client_text, parse_mode="Markdown")
        
        # 2. Формуємо сповіщення для водіїв
        driver_text = (
            "🚨 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!** 🚨\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n"
            f"👤 **Клієнт:** {user_name} (ID: {user_id})"
        )
        
        # Відправляємо в групу водіїв, якщо ID вказано в змінних Railway
        if DRIVER_CHAT_ID:
            await bot.send_message(chat_id=DRIVER_CHAT_ID, text=driver_text, parse_mode="Markdown")
        else:
            logging.warning("⚠️ DRIVER_CHAT_ID не налаштовано у змінних середовища Railway!")
            
    except Exception as e:
        logging.error(f"Помилка обробки даних з WebApp: {e}")
        await message.answer("⚠️ Сталася помилка при замовленні. Спробуйте ще раз.")

async def main():
    logging.info("Бот запущено...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
