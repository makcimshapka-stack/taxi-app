import asyncio
import json
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "8895482400:AAECLb1186EcGMi5laXwO3DYWayckFJ-dIk"
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/"

# Впишіть сюди реальний ID чату водіїв (наприклад, -1001234567890). 
# Якщо його ще немає, поки що для тесту можете вписати сюди свій власний числовий ID у Telegram, щоб замовлення припадали вам у приватні повідомлення.
DRIVERS_CHAT_ID = -1002456789123  # Змініть на свій ID або ID групи водіїв!

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

# Обробник даних, які надсилає міні-додаток (WebApp)
@dp.message(F.web_app_data)
async def web_app_order_handler(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        address_from = data.get("address_from", "Центр")
        address_to = data.get("address_to", "Не вказано")
        
        user_id = message.from_user.id
        user_name = message.from_user.full_name
        user_username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"

        # 1. Відправляємо підтвердження клієнту в його чат із ботом
        await message.answer(
            f"✅ **Ваше замовлення прийнято!**\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n\n"
            f"⏳ Шукаємо для вас вільного водія...",
            parse_mode="Markdown"
        )

        # 2. Формуємо кнопки для водіїв: Прийняти / Відхилити
        drivers_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Прийняти", callback_data=f"accept_{user_id}"),
                    InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{user_id}")
                ]
            ]
        )

        # Текст замовлення для чату водіїв
        driver_text = (
            f"🚖 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!**\n\n"
            f"👤 **Клієнт:** {user_name} ({user_username})\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}"
        )

        # Відправляємо замовлення у чат водіїв
        if DRIVERS_CHAT_ID:
            await bot.send_message(
                chat_id=DRIVERS_CHAT_ID, 
                text=driver_text, 
                reply_markup=drivers_keyboard, 
                parse_mode="Markdown"
            )
        else:
            # Якщо ID чату водіїв не налаштовано, надішлемо розробнику (вам) для перевірки
            await message.answer(
                f"⚠️ *Увага для адміна:* Не вказано `DRIVERS_CHAT_ID` в коді бота, тому водії не отримали замовлення.\n\n{driver_text}", 
                parse_mode="Markdown"
            )

    except Exception as e:
        logging.error(f"Помилка: {e}")
        await message.answer("Сталася помилка при оформленні замовлення. Спробуйте ще раз.")

# Обробка натискання кнопок водіями ("Прийняти" / "Відхилити")
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("reject_"))
async def driver_action_handler(callback: CallbackQuery):
    action, client_id_str = callback.data.split("_")
    client_id = int(client_id_str)
    driver_name = callback.from_user.full_name

    if action == "accept":
        # Змінюємо текст у чаті водіїв
        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            f"✅ **Замовлення прийняв водій:** {driver_name}",
            parse_mode="Markdown"
        )
        # Повідомляємо клієнта в його особистому чаті з ботом
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
