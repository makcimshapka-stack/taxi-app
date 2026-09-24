import asyncio
import json
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Вставте сюди токен вашого бота від @BotFather
TOKEN = "ТУТ_ВАШ_ТОКЕН_БОТА"

# Посилання на ваш створений сайт на GitHub Pages (index.html)
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/"

# ID чату водіїв (якщо потрібно пересилати замовлення в групу, впишіть сюди ID, наприклад: -1001234567890)
# Якщо поки що не потрібно, залиште None
DRIVERS_CHAT_ID = None

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    # Створюємо кнопку з веб-додатком (картою)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗺 Відкрити карту та замовити",
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    
    await message.answer(
        "👋 Вітаємо у службі таксі!\n\n"
        "Натисніть кнопку нижче, щоб відкрити мапу, обрати маршрут і викликати машину:",
        reply_markup=keyboard
    )

# Обробник отримання даних з міні-додатка (Web App)
@dp.message(F.web_app_data)
async def web_app_order_handler(message: Message):
    try:
        # Розпаковуємо JSON, який прилетів з карти
        data = json.loads(message.web_app_data.data)
        address_from = data.get("address_from", "Центр")
        address_to = data.get("address_to", "Не вказано")
        user_name = message.from_user.full_name
        user_phone = message.from_user.username or message.from_user.id

        # Формуємо текст замовлення для пасажира
        client_text = (
            f"✅ **Ваше замовлення прийнято!**\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n\n"
            f"Шукаємо для вас найближчого водія 🚗"
        )
        await message.answer(client_text, parse_mode="Markdown")

        # Формуємо текст для водіїв
        driver_text = (
            f"🚖 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!**\n\n"
            f"👤 **Клієнт:** {user_name} (@{user_phone})\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}"
        )

        # Якщо вказано ID чату водіїв, відправляємо туди
        if DRIVERS_CHAT_ID:
            await bot.send_message(chat_id=DRIVERS_CHAT_ID, text=driver_text, parse_mode="Markdown")
            
    except Exception as e:
        logging.error(f"Помилка обробки замовлення: {e}")
        await message.answer("Сталася помилка при обробці замовлення. Спробуйте ще раз.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
