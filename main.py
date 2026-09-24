import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

TOKEN = os.getenv("BOT_TOKEN")
DRIVER_CHAT_ID = os.getenv("DRIVER_CHAT_ID", "same")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🚗 Замовити таксі",
                    web_app=WebAppInfo(url="https://makcimshapka-stack.github.io/taxi-app/?v=8")
                )
            ]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Вітаємо у службі таксі Кобеляки!\nНатисніть кнопку нижче, щоб вибрати маршрут на мапі:",
        reply_markup=keyboard
    )

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        from_addr = data.get("address_from", "Не вказано")
        to_addr = data.get("address_to", "Не вказано")
        passenger_name = message.from_user.full_name
        username = message.from_user.username
        passenger_username = f"@{username}" if username else "немає"
        
        # Повідомлення пасажиру
        await message.answer(f"✅ Ваше замовлення прийнято!\n📍 Звідки: {from_addr}\n🏁 Куди: {to_addr}\n\nШукаємо водія...")

        # Клавіатура для водія
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Взяти замовлення", callback_data="accept_order")]
        ])

        driver_text = (
            f"🚨 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!** 🚨\n\n"
            f"👤 Пасажир: {passenger_name} ({passenger_username})\n"
            f"📍 Звідки: {from_addr}\n"
            f"🏁 Куди: {to_addr}"
        )

        target_chat = DRIVER_CHAT_ID if DRIVER_CHAT_ID != "same" else message.chat.id
        await bot.send_message(target_chat, driver_text, reply_markup=kb, parse_mode="Markdown")

    except Exception as e:
        await message.answer("Сталася помилка при обробці замовлення.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
