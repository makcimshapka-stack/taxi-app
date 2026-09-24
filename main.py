import os
import json
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Message, CallbackQuery
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DRIVER_CHAT_ID = os.getenv("DRIVER_CHAT_ID")

if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/?v=109"

# Сховище номерів телефонов клієнтів
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
            "Для роботи служби таксі та зв'язку з водіями, будь ласка, натисніть кнопку нижче та поділіться номером телефону:",
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
                    text="🚖 Замовити таксі на мапі", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    await message.answer("Натисніть кнопку нижче, щоб відкрити інтерактивну карту Кобеляк:", reply_markup=keyboard)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get("action") == "new_order":
            address_from = data.get("address_from", "Центр (Кобеляки)")
            address_to = data.get("address_to", "Не вказано")
            lat = data.get("lat", 49.1445)
            lng = data.get("lng", 34.1906)
            
            user_name = message.from_user.first_name
            user_id = message.from_user.id
            phone = user_phones.get(user_id, "Не вказано")
            
            # Підтвердження клієнту
            await message.answer(
                "✅ **Ваше замовлення прийнято в пошук!**\n\n"
                f"📍 **Звідки:** {address_from}\n"
                f"🏁 **Куди:** {address_to}\n\n"
                "Очікуємо, поки водій прийме замовлення...",
                parse_mode="Markdown"
            )
            
            # Кнопка для водіїв (ховаємо lat, lng, phone та user_id в callback_data)
            driver_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Прийняти замовлення", 
                            callback_data=f"acc_{user_id}_{lat}_{lng}"
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
            
            if DRIVER_CHAT_ID:
                await bot.send_message(
                    chat_id=DRIVER_CHAT_ID, 
                    text=driver_text, 
                    reply_markup=driver_keyboard, 
                    parse_mode="Markdown"
                )
            
    except Exception as e:
        logging.error(f"Помилка обробки WebApp: {e}")
        await message.answer("⚠️ Сталася помилка при замовленні.")

@dp.callback_query(F.data.startswith("acc_"))
async def accept_order(callback: CallbackQuery):
    parts = callback.data.split("_")
    client_id = int(parts[1])
    lat = parts[2]
    lng = parts[3]
    
    driver_name = callback.from_user.first_name
    driver_id = callback.from_user.id
    phone = user_phones.get(client_id, "Не вказано")
    
    try:
        # Сповіщаємо клієнта
        await bot.send_message(
            chat_id=client_id,
            text=f"🚗 **Ваше замовлення прийнято!** Водій **{driver_name}** виїжджає до вас.",
            parse_mode="Markdown"
        )
        
        # Навігація для водія прямо до точок клієнта
        nav_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        nav_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🗺 Навігація до клієнта (Google Maps)", 
                        url=nav_url
                    )
                ]
            ]
        )
        
        # Надсилаємо водію в ЛС інформацію і навігацію
        try:
            await bot.send_message(
                chat_id=driver_id,
                text=f"📌 **Маршрут прийнято!**\n📞 Телефон клієнта: `{phone}`",
                reply_markup=nav_keyboard,
                parse_mode="Markdown"
            )
        except:
            pass
        
        # Оновлюємо повідомлення в групі
        new_text = callback.message.text + f"\n\n✅ **Статус:** Прийняв(ла) — **{driver_name}**\n📞 Тел: `{phone}`"
        await callback.message.edit_text(text=new_text, reply_markup=None, parse_mode="Markdown")
        await callback.answer("Ви успішно прийняли замовлення!")
        
    except Exception as e:
        logging.error(f"Помилка прийняття: {e}")
        await callback.answer("⚠️ Помилка обробки.", show_alert=True)

async def main():
    logging.info("Бот запущено...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
