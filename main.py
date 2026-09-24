import os
import json
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
DRIVER_CHAT_ID = os.getenv("DRIVER_CHAT_ID")  # ID чату водіїв (наприклад, -1001234567890)
PORT = int(os.getenv("PORT", 8080))          # Порт, який виділяє Railway

if not TOKEN:
    raise ValueError("Помилка: BOT_TOKEN не знайдено!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# URL вашого сайту на GitHub Pages
WEB_APP_URL = "https://makcimshapka-stack.github.io/taxi-app/?v=106"

@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚖 Замовити таксі (Карта)", 
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    
    welcome_text = (
        f"Вітаю, {message.from_user.first_name}! 👋\n\n"
        "Це офіційний бот служби таксі в Кобеляках.\n"
        "Натисніть кнопку нижче, щоб відкрити карту та оформити замовлення:"
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)

# HTTP-сервер для приймання замовлень прямо з сайту
async def handle_order(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        user_name = data.get("user_name", "Клієнт")
        address_from = data.get("address_from", "Не вказано")
        address_to = data.get("address_to", "Не вказано")

        if not user_id:
            return web.json_response({"status": "error", "message": "No user_id"}, status=400)

        # 1. Повідомлення клієнту в особисті
        client_text = (
            "✅ **Ваше замовлення прийнято в роботу!**\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n\n"
            "Очікуйте, шукаємо вільне авто..."
        )
        await bot.send_message(chat_id=int(user_id), text=client_text, parse_mode="Markdown")

        # 2. Повідомлення у групу водіїв
        driver_text = (
            "🚨 **НОВЕ ЗАМОВЛЕННЯ!** 🚨\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n"
            f"👤 **Клієнт:** {user_name} (ID: {user_id})"
        )
        
        if DRIVER_CHAT_ID:
            await bot.send_message(chat_id=DRIVER_CHAT_ID, text=driver_text, parse_mode="Markdown")

        return web.json_response({"status": "ok"})
    except Exception as e:
        logging.error(f"Помилка в HTTP обробнику: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def web_server():
    app = web.Application()
    app.router.add_post('/api/order', handle_order)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"HTTP сервер запущено на порті {PORT}")

async def main():
    # Запускаємо одночасно Telegram бота та веб-сервер
    await asyncio.gather(
        dp.start_polling(bot),
        web_server()
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
