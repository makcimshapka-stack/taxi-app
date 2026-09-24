import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "8895482400:AAECLb1186EcGMi5laXwO3DYWayckFJ-dIk"
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/"
DRIVERS_CHAT_ID = -1002456789123  # Замініть на ID групи водіїв або свій ID для тестів

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
        "Натисніть кнопку нижче, щоб відкрити карту, обрати звідки та куди їхати:",
        reply_markup=keyboard
    )

# Ловимо текст замовлення, який передається з міні-додатка
@dp.message(F.text.startswith("🚖 Замовлення таксі:"))
async def process_text_order(message: Message):
    try:
        lines = message.text.split("\n")
        address_from = lines[1].replace("📍 Звідки: ", "") if len(lines) > 1 else "Центр"
        address_to = lines[2].replace("🏁 Куди: ", "") if len(lines) > 2 else "Не вказано"

        user_id = message.from_user.id
        user_name = message.from_user.full_name
        user_username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"

        # Підтвердження клієнту
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
        logging.error(f"Помилка обробки замовлення: {e}")
        await message.answer("Сталася помилка при замовленні. Спробуйте ще раз.")

# Обробка натискання кнопок водіями
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("reject_"))
async def driver_action_handler(callback: CallbackQuery):
    action, client_id_str = callback.data.split("_")
    client_id = int(client_id_str)
    driver_name = callback.from_user.full_name

    if action == "accept":
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
