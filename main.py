import asyncio
import json
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "8895482400:AAECLb1186EcGMi5laXwO3DYWayckFJ-dIk"
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/"
DRIVERS_CHAT_ID = -1002456789123  # Замініть на свій ID або ID групи водіїв

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
        "👋 Вітаємо у службі таксі Кобеляки!\n\n"
        "Натисніть кнопку нижче, щоб відкрити карту та викликати машину:",
        reply_markup=keyboard
    )

# Обробник даних, які надсилає міні-додаток через tg.sendData()
@dp.message(F.web_app_data)
async def web_app_order_handler(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        address_from = data.get("address_from", "Центр")
        address_to = data.get("address_to", "Не вказано")
        
        user_id = message.from_user.id
        user_name = message.from_user.full_name
        user_username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"

        # Повідомлення клієнту
        await message.answer(
            f"✅ **Ваше замовлення прийняте!**\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n\n"
            f"⏳ Шукаємо вільного водія...",
            parse_mode="Markdown"
        )

        # Кнопки для водіїв у чаті водіїв
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

        if DRIVERS_CHAT_ID:
            await bot.send_message(
                chat_id=DRIVERS_CHAT_ID,
                text=driver_text,
                reply_markup=drivers_keyboard,
                parse_mode="Markdown"
            )

    except Exception as e:
        logging.error(f"Помилка WebApp даних: {e}")
        await message.answer("Сталася помилка при замовленні. Спробуйте ще раз.")

# Обробка натискання кнопок водіями
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("reject_"))
async def driver_action_handler(callback: CallbackQuery):
    action, client_id_str = callback.data.split("_")
    client_id = int(client_id_str)
    driver_name = callback.from_user.full_name

3    if action == "accept":
        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            f"✅ **Замовлення прийняв водій:** {driver_name}",
            parse_mode="Markdown"
        )
        try:
            await bot.send_message(
                chat_id=client_id,
                text=f"🎉 **Ваш водій знайшовся!**\n🚗 Водій *{driver_name}* прийняв замовлення та вже їде до вас!",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await callback.answer("Ви успішно прийняли замовлення!")

    elif action == "reject":
        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            f"❌ **Замовлення відхилено водієм ({driver_name})**",
            parse_mode="Markdown"
        )
        await callback.answer("Ви відхилили замовлення.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
