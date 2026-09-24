import os
import json
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DRIVER_CHAT_ID = os.getenv("DRIVER_CHAT_ID")

if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/?v=107"

@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚖 Замовити таксі", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    
    welcome_text = (
        f"Вітаю, {message.from_user.first_name}! 👋\n\n"
        "Це офіційний бот служби таксі в Кобеляках.\n"
        "Натисніть кнопку нижче, щоб відкрити замовлення:"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get("action") == "new_order":
            address_from = data.get("address_from", "Не вказано")
            address_to = data.get("address_to", "Не вказано")
            user_name = message.from_user.first_name
            user_id = message.from_user.id
            
            # Підтвердження клієнту в особисті
            client_text = (
                "✅ **Ваше замовлення прийнято в пошук!**\n\n"
                f"📍 **Звідки:** {address_from}\n"
                f"🏁 **Куди:** {address_to}\n\n"
                "Очікуємо, поки водій прийме замовлення..."
            )
            await message.answer(client_text, parse_mode="Markdown")
            
            # Кнопка для водіїв (ховаємо всередині callback_data ID клієнта)
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
            
            # Повідомлення для групи водіїв
            driver_text = (
                "🚨 **НОВЕ ЗАМОВЛЕННЯ!** 🚨\n\n"
                f"📍 **Звідки:** {address_from}\n"
                f"🏁 **Куди:** {address_to}\n"
                f"👤 **Клієнт:** {user_name}"
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
    client_id = int(callback.data.split("_")[1])
    
    try:
        # Сповіщаємо клієнта в особисті повідомлення
        await bot.send_message(
            chat_id=client_id,
            text=f"🚗 **Ваше замовлення прийнято!** Водій **{driver_name}** виїжджає до вас. Очікуйте авто.",
            parse_mode="Markdown"
        )
        
        # Оновлюємо повідомлення в групі водіїв (прибираємо кнопку і пишемо, хто прийняв)
        new_text = callback.message.text + f"\n\n✅ **Статус:** Замовлення прийняв(ла) — **{driver_name}**"
        await callback.message.edit_text(text=new_text, reply_markup=None, parse_mode="Markdown")
        await callback.answer("Ви успішно прийняли замовлення!")
        
    except Exception as e:
        logging.error(f"Помилка при прийнятті замовлення: {e}")
        await callback.answer("⚠️ Не вдалося зв'язатися з клієнтом або замовлення вже застаріло.", show_alert=True)

async def main():
    logging.info("Бот запущено...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
