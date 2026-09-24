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

# Замініть посилання на ваше актуальне з GitHub Pages (можете залишити з вашою версією)
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/?v=106"

@dp.message(Command("start"))
async def cmd_start(message: Message):
    # Використовуємо тільки інлайн-кнопку для відкриття веб-додатка
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
    
    # Видаляємо старі клавіатури, якщо вони лишилися в історії, і надсилаємо чисте повідомлення
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get("action") == "new_order":
            address_from = data.get("address_from", "Не вказано")
            address_to = data.get("address_to", "Не вказано")
            user_name = message.from_user.first_name
            
            # Відповідь клієнту в особисті повідомлення
            client_text = (
                "✅ **Ваше замовлення прийнято в роботу!**\n\n"
                f"📍 **Звідки:** {address_from}\n"
                f"🏁 **Куди:** {address_to}\n\n"
                "Очікуйте, шукаємо вільне авто..."
            )
            await message.answer(client_text, parse_mode="Markdown")
            
            # Повідомлення для групи водіїв
            driver_text = (
                "🚨 **НОВЕ ЗАМОВЛЕННЯ!** 🚨\n\n"
                f"📍 **Звідки:** {address_from}\n"
                f"🏁 **Куди:** {address_to}\n"
                f"👤 **Клієнт:** {user_name}"
            )
            
            # Відправляємо в групу водіїв, якщо вказано ID
            if DRIVER_CHAT_ID:
                await bot.send_message(chat_id=DRIVER_CHAT_ID, text=driver_text, parse_mode="Markdown")
            else:
                logging.warning("⚠️ DRIVER_CHAT_ID не налаштовано в змінних середовища Railway!")
            
    except Exception as e:
        logging.error(f"Помилка обробки даних з WebApp: {e}")
        await message.answer("⚠️ Сталася помилка при замовленні. Спробуйте ще раз.")

async def main():
    logging.info("Бот запущено...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
