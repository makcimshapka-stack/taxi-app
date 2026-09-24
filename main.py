import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🚗 Замовити таксі",
                    web_app=WebAppInfo(url="https://makcimshapka-stack.github.io/taxi-app/?v=6")
                )
            ]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Привіт! Натисніть кнопку нижче, щоб відкрити карту та замовити таксі в Кобеляках:",
        reply_markup=keyboard
    )

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        from_addr = data.get("address_from", "Не вказано")
        to_addr = data.get("address_to", "Не вказано")
        
        await message.answer(
            f"✅ Замовлення прийнято!\n\n📍 Звідки: {from_addr}\n🏁 Куди: {to_addr}"
        )
    except Exception as e:
        await message.answer("Помилка при обробці замовлення.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
