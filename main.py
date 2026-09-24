import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

TOKEN = os.getenv("BOT_TOKEN")
DRIVER_CHAT_ID = os.getenv("DRIVER_CHAT_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Зберігаємо номери телефонів користувачів у пам'яті
user_phones = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Кнопка для запиту номера телефону
    contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поділитися номером телефону", request_contact=True)],
            [KeyboardButton(text="🚗 Замовити таксі", web_app=WebAppInfo(url="https://makcimshapka-stack.github.io/taxi-app/?v=8"))]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Вітаємо у службі таксі Кобеляки!\nБудь ласка, поділіться вашим номером телефону для зв'язку, а потім натисніть «Замовити таксі»:",
        reply_markup=contact_keyboard
    )

@dp.message(F.contact)
async def contact_handler(message: types.Message):
    if message.contact:
        user_phones[message.from_user.id] = message.contact.phone_number
        await message.answer("✅ Дякуємо! Ваш номер збережено. Тепер натисніть «Замовити таксі».", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🚗 Замовити таксі", web_app=WebAppInfo(url="https://makcimshapka-stack.github.io/taxi-app/?v=8"))]],
            resize_keyboard=True
        ))

@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        from_addr = data.get("address_from", "Не вказано")
        to_addr = data.get("address_to", "Не вказано")
        passenger_name = message.from_user.full_name
        username = message.from_user.username
        passenger_username = f"@{username}" if username else "немає"
        phone = user_phones.get(message.from_user.id, "Не вказано (не передано)")
        
        # Повідомлення пасажиру
        await message.answer(f"✅ Ваше замовлення прийнято!\n📍 Звідки: {from_addr}\n🏁 Куди: {to_addr}\n📞 Телефон: {phone}\n\nШукаємо водія...")

        # Клавіатура для водія
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Взяти замовлення", callback_data="accept_order"),
                InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_order")
            ]
        ])

        driver_text = (
            f"🚨 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!** 🚨\n\n"
            f"👤 Пасажир: {passenger_name} ({passenger_username})\n"
            f"📞 Телефон: `{phone}`\n"
            f"📍 Звідки: {from_addr}\n"
            f"🏁 Куди: {to_addr}"
        )

        target_chat = DRIVER_CHAT_ID if DRIVER_CHAT_ID else message.chat.id
        await bot.send_message(int(target_chat), driver_text, reply_markup=kb, parse_mode="Markdown")

    except Exception as e:
        await message.answer("✅ Замовлення передано водіям!")

@dp.callback_query(F.data.in_(["accept_order", "cancel_order"]))
async def callback_handler(callback: types.CallbackQuery):
    driver_name = callback.from_user.full_name
    if callback.data == "accept_order":
        new_text = callback.message.text + f"\n\n🟢 **Статус:** Взяв водій: {driver_name}"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"✅ Виконує {driver_name}", callback_data="taken")]
        ])
        await callback.message.edit_text(new_text, reply_markup=kb, parse_mode="Markdown")
        await callback.answer("Ви успішно взяли замовлення!")
    elif callback.data == "cancel_order":
        new_text = callback.message.text + f"\n\n🔴 **Статус:** Замовлення скасовано ({driver_name})"
        await callback.message.edit_text(new_text, parse_mode="Markdown")
        await callback.answer("Замовлення скасовано.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
