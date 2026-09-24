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

WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/?v=108"

# Тимчасове сховище номерів телефонів клієнтів (в пам'яті бота)
user_phones = {}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    # Якщо телефон ще не збережено, просимо поділитися контактом
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
            "Щоб користуватися службою таксі та для зв'язку з водіями, будь ласка, поділіться своїм номером телефону:",
            reply_markup=request_phone_keyboard
        )
    else:
        await send_main_menu(message)

@dp.message(F.contact)
async def handle_contact(message: Message):
    if message.contact:
        user_phones[message.from_user.id] = message.contact.phone_number
        # Прибираємо клавіатуру запиту номера і показуємо кнопку замовлення
        await message.answer("✅ Дякуємо! Номер успішно збережено.", reply_markup=types.ReplyKeyboardRemove())
        await send_main_menu(message)

async def send_main_menu(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚖 Замовити таксі (Відкрити карту)", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    await message.answer("Натисніть кнопку нижче, щоб обрати маршрут на мапі Кобеляк:", reply_markup=keyboard)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get("action") == "new_order":
            address_from = data.get("address_from", "Центр (Кобеляки)")
            address_to = data.get("address_to", "Не вказано")
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
            
            # Кнопка для водіїв
            driver_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Прийняти замовлення", 
                            callback_data=f"accept_{user_id}"
                        )
                    ]
                ]
            )
            
            # Повідомлення для групи водіїв (містить адресу і телефон)
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
            else:
                logging.warning("⚠️ DRIVER_CHAT_ID не налаштовано!")
            
    except Exception as e:
        logging.error(f"Помилка обробки WebApp даних: {e}")
        await message.answer("⚠️ Сталася помилка при замовленні.")

# Обробка натискання кнопки водієм
@dp.callback_query(F.data.startswith("accept_"))
async def accept_order(callback: CallbackQuery):
    driver_name = callback.from_user.first_name
    driver_id = callback.from_user.id
    client_id = int(callback.data.split("_")[1])
    phone = user_phones.get(client_id, "Не вказано")
    
    try:
        # Сповіщаємо клієнта
        await bot.send_message(
            chat_id=client_id,
            text=f"🚗 **Ваше замовлення прийнято!** Водій **{driver_name}** виїжджає до вас.",
            parse_mode="Markdown"
        )
        
        # Посилання на навігацію для водія (універсальні координати центру Кобеляк або назва)
        map_link = f"https://maps.google.com/?q={urllib_quote(address_from) if 'address_from' in locals() else 'Kobelyaky'}"
        
        # Кнопка навігації для водія в особисті або просто в тексті
        nav_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🗺 Відкрити маршрут у Google Maps", 
                        url=f"https://www.google.com/maps/search/?api=1&query=Kobelyaky"
                    )
                ]
            ]
        )
        
        # Відправляємо водію контакти клієнта та навігацію в особисті повідомлення (якщо він писав боту) або дублюємо в чат
        try:
            await bot.send_message(
                chat_id=driver_id,
                text=f"📌 **Маршрут замовлення:**\n📍 Звідки: клієнт чекає\n📞 Телефон клієнта: `{phone}`",
                reply_markup=nav_keyboard,
                parse_mode="Markdown"
            )
        except:
            pass # Якщо водій не запускав бота в ЛС, нічого страшного
        
        # Оновлюємо повідомлення в групі водіїв
        new_text = callback.message.text + f"\n\n✅ **Статус:** Прийняв(ла) — **{driver_name}**\n📞 Тел клієнта: `{phone}`"
        await callback.message.edit_text(text=new_text, reply_markup=None, parse_mode="Markdown")
        await callback.answer("Ви успішно прийняли замовлення!")
        
    except Exception as e:
        logging.error(f"Помилка при прийнятті замовлення: {e}")
        await callback.answer("⚠️ Помилка обробки замовлення.", show_alert=True)

async def main():
    logging.info("Бот запущено...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
