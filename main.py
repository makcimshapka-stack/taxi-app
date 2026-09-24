import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "8895482400:AAECLb1186EcGMi5laXwO3DYWayckFJ-dIk"
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/"
DRIVERS_CHAT_ID = None # Сюди можна вписати ID групи водіїв, наприклад -100xxxxxxxxxx

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message):
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

# Обробник замовлення, яке надходить із сайту
@dp.message(F.text.startswith("🚖 Замовлення таксі"))
async def process_taxi_order(message: Message):
    user_name = message.from_user.full_name
    user_contact = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"

    # Відправляємо підтвердження клієнту
    await message.answer(
        f"✅ **Ваше замовлення прийнято!**\n\n"
        f"{message.text}\n\n"
        f"Шукаємо для вас найближчого водія 🚗",
        parse_mode="Markdown"
    )

    # Формуємо повідомлення для водіїв
    driver_text = (
        f"🚨 **НОВЕ ЗАМОВЛЕННЯ!**\n\n"
        f"👤 **Клієнт:** {user_name} ({user_contact})\n"
        f"{message.text}"
    )

    # Якщо вказано ID чату водіїв, надсилаємо туди
    if DRIVERS_CHAT_ID:
        await bot.send_message(chat_id=DRIVERS_CHAT_ID, text=driver_text, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
