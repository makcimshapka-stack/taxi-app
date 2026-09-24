import os
import json
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery
from aiogram.filters import Command

# Налаштування логування
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DRIVER_CHAT_ID = os.getenv("DRIVER_CHAT_ID")  # ID чату водіїв (наприклад, -100xxxxxxxxxx)

if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено у змінних середовища!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Посилання на вашу оновлену мапу на GitHub
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/map2.html"

# Словник для збереження телефонів користувачів
user_phones = {}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if user_id not in user_phones:
        request_phone_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📱 Поділитися номером телефону", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            f"Вітаю, {message.from_user.first_name}! 👋\n\n"
            "Для виклику таксі, будь ласка, поділіться номером телефону:",
            reply_markup=request_phone_keyboard
        )
    else:
        await send_main_menu(message)

@dp.message(F.contact)
async def handle_contact(message: Message):
    if message.contact:
        user_phones[message.from_user.id] = message.contact.phone_number
        await message.answer("✅ Дякуємо! Номер успішно збережено.", reply_markup=types.ReplyKeyboardRemove())
        await send_main_menu(message)

async def send_main_menu(message: Message):
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
    await message.answer("Натисніть кнопку нижче, щоб відкрити мапу та вказати маршрут:", reply_markup=keyboard)

# Головний обробник даних від WebApp (коли користувач натискає «Замовити таксі»)
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get("action") == "new_order":
            address_from = data.get("address_from", "Не вказано")
            address_to = data.get("address_to", "Не вказано")
            
            user_name = message.from_user.first_name
            user_id = message.from_user.id
            phone = user_phones.get(user_id, "Не вказано")
            
            # Повідомлення клієнту
            await message.answer(
                "✅ **Ваше замовлення прийнято в пошук!**\n\n"
                f"📍 **Звідки:** {address_from}\n"
                f"🏁 **Куди:** {address_to}\n\n"
                "Очікуємо на водія...",
                parse_mode="Markdown"
            )
            
            # Кнопка для водіїв щоб прийняти замовлення
            driver_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Прийняти замовлення", 
                            callback_data=f"acc_{user_id}"
                        )
                    ]
                ]
            )
            
            driver_text = (
                "🚨 **НОВЕ ЗАМОВЛЕННЯ!** 🚨\n\n"
                f"📍 **Звідки:** {address_from}\n"
                f"🏁 **Куди:** {address_to}\n"
                f"👤 **Клієнт:** {user_name}\n"
                f"📞 **Телефон:** `{phone}`"
            )
            
            # Надсилаємо у чат водіїв
            if DRIVER_CHAT_ID:
                await bot.send_message(
                    chat_id=int(DRIVER_CHAT_ID), 
                    text=driver_text, 
                    reply_markup=driver_keyboard, 
                    parse_mode="Markdown"
                )
            else:
                logging.warning("DRIVER_CHAT_ID не задано в середовищі Railway!")
            
    except Exception as e:
        logging.error(f"Помилка обробки WebApp даних: {e}")
        await message.answer("⚠️ Сталася помилка при оформленні замовлення.")

# Обробка натискання водієм кнопки «Прийняти замовлення»
@dp.callback_query(F.data.startswith("acc_"))
async def accept_order(callback: CallbackQuery):
    parts = callback.data.split("_")
    client_id = int(parts[1])
    driver_name = callback.from_user.first_name
    phone = user_phones.get(client_id, "Не вказано")
    
    try:
        # Повідомлення клієнту про те, що водій їде
        await bot.send_message(
            chat_id=client_id,
            text=f"🚗 **Замовлення прийнято!** Водій **{driver_name}** виїжджає до вас.",
            parse_mode="Markdown"
        )
        
        new_text = (
            callback.message.text + 
            f"\n\n✅ **Статус:** Прийняв(ла) — **{driver_name}**\n"
            f"📞 **Тел. клієнта:** `{phone}`"
        )
        
        # Оновлюємо текст у чаті водіїв
        await callback.message.edit_text(
            text=new_text, 
            parse_mode="Markdown"
        )
        await callback.answer("Ви успішно прийняли замовлення!")
        
    except Exception as e:
        logging.error(f"Помилка при прийнятті замовлення: {e}")
        await callback.answer("⚠️ Помилка обробки замовлення.", show_alert=True)

async def main():
    logging.info("Бот запущено та готовий до роботи...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
