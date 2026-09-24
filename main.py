import asyncio
import json
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, 
    CallbackQuery, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    WebAppInfo, 
    ReplyKeyboardMarkup, 
    KeyboardButton
)

# Вставте ваш токен бота та ID чату водіїв
TOKEN = "ТУТ_ВАШ_ТОКЕН_БОТА"
DRIVERS_CHAT_ID = -1001234567890  # Замініть на реальний ID чату або каналу водіїв (ціле число з мінусом)

# URL вашого веб-додатка (GitHub Pages або інший хостинг, де лежить index.html)
WEB_APP_URL = "https://ваш-username.github.io/репозиторій/"

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Стартове меню з кнопкою відкриття мапи (WebApp)
@dp.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🚖 Відкрити карту та замовити", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "👋 Вітаємо у службі таксі Кобеляки!\n\n"
        "Натисніть кнопку нижче, щоб відкрити карту, обрати звідки та куди їхати:",
        reply_markup=keyboard
    )

# ГОЛОВНИЙ ОБРОБНИК: Ловимо дані, які надсилає міні-додаток через tg.sendData()
@dp.message(F.web_app_data)
async def web_app_order_handler(message: Message):
    try:
        # Розпаковуємо JSON, який надійшов із JavaScript (index.html)
        data = json.loads(message.web_app_data.data)
        address_from = data.get("address_from", "Центр (Кобеляки)")
        address_to = data.get("address_to", "Не вказано")

        user_id = message.from_user.id
        user_name = message.from_user.full_name
        user_username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"

        # 1. Надсилаємо підтвердження клієнту в чат
        await message.answer(
            f"✅ **Ваше замовлення прийняте!**\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n\n"
            f"⏳ Шукаємо вільного водія...",
            parse_mode="Markdown"
        )

        # 2. Формуємо кнопки для водіїв
        drivers_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Прийняти", callback_data=f"accept_{user_id}"),
                    InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{user_id}")
                ]
            ]
        )

        driver_text = (
            f"🚨 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!**\n\n"
            f"👤 **Клієнт:** {user_name} ({user_username})\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}"
        )

        # 3. Пересилаємо замовлення у робочий чат водіїв
        if DRIVERS_CHAT_ID:
            await bot.send_message(
                chat_id=DRIVERS_CHAT_ID,
                text=driver_text,
                reply_markup=drivers_keyboard,
                parse_mode="Markdown"
            )

    except Exception as e:
        logging.error(f"Помилка обробки WebApp даних: {e}")
        await message.answer("Сталася помилка при обробці замовлення. Спробуйте ще раз натиснути кнопку замовлення.")

# Обробка натискання кнопки водієм «Прийняти»
@dp.callback_query(F.data.startswith("accept_"))
async def driver_accept_order(callback: CallbackQuery):
    client_id = int(callback.data.split("_")[1])
    driver_name = callback.from_user.full_name

    try:
        # Повідомляємо клієнта, що водій знайшовся
        await bot.send_message(
            chat_id=client_id,
            text=f"🎉 **Ваше замовлення прийнято!** Водій *{driver_name}* виїжджає.",
            parse_mode="Markdown"
        )
        
        # Оновлюємо повідомлення у чаті водіїв
        await callback.message.edit_text(
            callback.message.text + f"\n\n✅ **Замовлення прийняв:** {driver_name}",
            parse_mode="Markdown"
        )
        await callback.answer("Ви успішно прийняли замовлення!")
    except Exception as e:
        await callback.answer("Помилка: можливо, клієнт заблокував бота.", show_alert=True)

# Обробка натискання кнопки водієм «Відхилити»
@dp.callback_query(F.data.startswith("reject_"))
async def driver_reject_order(callback: CallbackQuery):
    await callback.message.edit_text(
        callback.message.text + f"\n\n❌ **Скасовано водієм** ({callback.from_user.full_name})",
        parse_mode="Markdown"
    )
    await callback.answer("Ви відхилили замовлення.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
