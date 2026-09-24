import os
import json
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DRIVER_CHAT_ID = os.getenv("DRIVER_CHAT_ID") # Наприклад: "-1001234567890"

if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Посилання на ваш сайт у GitHub Pages
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/?v=106"

@dp.message(Command("start"))
async def cmd_start(message: Message):
    # Кнопка відкриття веб-додатка знизу екрана
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🚗 Замовити таксі", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
    
    welcome_text = (
        f"Вітаю, {message.from_user.first_name}! 👋\n\n"
        "Це офіційний бот служби таксі в Кобеляках.\n"
        "Натисніть кнопку **«🚗 Замовити таксі»** внизу екрана, щоб відкрити карту:"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        address_from = data.get("address_from", "Не вказано")
        address_to = data.get("address_to", "Не вказано")
        user_name = message.from_user.first_name
        user_id = message.from_user.id
        
        # 1. Відправляємо підтвердження клієнту в особисті
        client_text = (
            "✅ **Ваше замовлення прийнято в роботу!**\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n\n"
            "⏳ Очікуйте, шукаємо вільне авто..."
        )
        await message.answer(client_text, parse_mode="Markdown")
        
        # 2. Формуємо інлайн-кнопки для водіїв у групі
        driver_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Прийняти", callback_data=f"accept_{user_id}"),
                    InlineKeyboardButton(text="❌ Відмовитись", callback_data=f"cancel_{user_id}")
                ]
            ]
        )
        
        driver_text = (
            "🚨 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!** 🚨\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n"
            f"👤 **Клієнт:** {user_name} (ID: {user_id})"
        )
        
        if DRIVER_CHAT_ID:
            await bot.send_message(
                chat_id=DRIVER_CHAT_ID, 
                text=driver_text, 
                reply_markup=driver_keyboard, 
                parse_mode="Markdown"
            )
        else:
            logging.warning("⚠️ DRIVER_CHAT_ID не налаштовано у змінних середовища Railway!")
            
    except Exception as e:
        logging.error(f"Помилка обробки даних з WebApp: {e}")
        await message.answer("⚠️ Сталася помилка при замовленні. Спробуйте ще раз.")

# Обробка натискань водіїв на кнопки «Прийняти» або «Відмовитись»
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("cancel_"))
async def handle_driver_action(callback: CallbackQuery):
    action, client_id = callback.data.split("_")
    driver_name = callback.from_user.first_name
    
    if action == "accept":
        new_text = callback.message.text + f"\n\n✅ **Статус:** Замовлення прийняв водій **{driver_name}**"
        # Видаляємо кнопки, щоб інші водії бачили, що замовлення вже зайняте
        await callback.message.edit_text(new_text, parse_mode="Markdown")
        await callback.answer(f"Ви прийняли замовлення!", show_alert=False)
        
        # Опційно: можна надіслати сповіщення клієнту, що водій знайшовся
        try:
            await bot.send_message(
                chat_id=int(client_id), 
                text=f"🚖 Водій **{driver_name}** прийняв ваше замовлення і виїжджає!", 
                parse_mode="Markdown"
            )
        except Exception:
            pass
            
    elif action == "cancel":
        new_text = callback.message.text + f"\n\n❌ **Статус:** Водій **{driver_name}** відмовився від замовлення."
        await callback.message.edit_text(new_text, parse_mode="Markdown")
        await callback.answer(f"Ви відмовилися від замовлення.", show_alert=False)

async def main():
    logging.info("Бот запущено...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
