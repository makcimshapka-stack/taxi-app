import logging
import asyncio
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types

API_TOKEN = '8895482400:AAF22IJsYMCOImngnkhXfjFml8X0Z5_sG4k'
DRIVER_CHAT_ID = -5357703122

DRIVERS_INFO = {
    "Макс": {"card": "4874070013052004", "car": "Chery Amulet (КЕ3389АК)", "display": "Макс"},
    "Артур": {"card": "4441114417805692", "car": "Renault", "display": "Артур"},
    "Троценко": {"card": "4149629378242937", "car": "Лада Гранта", "display": "Троценко"},
    "Валерій": {"card": "4149629378242937", "car": "Лада Гранта", "display": "Валерій"}
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
app = FastAPI()

class OrderSchema(BaseModel):
    user_id: int
    phone: str
    address_from: str
    address_to: str
    payment_method: str

@app.get("/", response_class=HTMLResponse)
async def serve_webapp():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Файл index.html не знайдено!</h1>"

@app.post("/order")
async def create_order(order: OrderSchema):
    order_text = (
        f"🚨 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!** 🚨\n\n"
        f"📍 **Звідки:** {order.address_from}\n"
        f"🏁 **Куди:** {order.address_to}\n"
        f"📞 **Телефон клієнта:** `{order.phone}`\n"
        f"💳 **Оплата:** {order.payment_method}\n"
    )
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🚗 Взяти замовлення", callback_data=f"accept_{order.user_id}_{order.payment_method}")]
        ]
    )
    await bot.send_message(DRIVER_CHAT_ID, order_text, reply_markup=markup, parse_mode="Markdown")
    return {"status": "ok"}

@dp.message(lambda message: message.text and message.text.startswith('/start'))
async def send_welcome(message: types.Message):
    railway_url = "https://Taxi-app-production-df59.up.railway.app/"
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🚗 Замовити таксі (Кобеляки)", web_app=types.WebAppInfo(url=railway_url))]
        ]
    )
    await message.answer("👋 Вітаємо у службі таксі Кобеляки!\nНатисніть кнопку нижче для замовлення:", reply_markup=markup)

@dp.callback_query(lambda c: c.data and c.data.startswith('accept_'))
async def process_accept(callback: types.CallbackQuery):
    parts = callback.data.split('_')
    client_id = int(parts[1])
    payment_method = parts[2] if len(parts) > 2 else "Готівка"
    
    first_name = callback.from_user.first_name or ""
    driver_data, driver_display_name = None, first_name

    for key, data in DRIVERS_INFO.items():
        if key.lower() in first_name.lower():
            driver_data, driver_display_name = data, data["display"]
            break
    
    if not driver_data:
        driver_data = {"card": "4149629378242937", "car": "Лада Гранта"}
        driver_display_name = first_name or "Водій"

    updated_text = callback.message.text + f"\n\n✅ **Замовлення прийняв(ла): {driver_display_name}**\n🚗 **Авто:** {driver_data['car']}"
    await callback.message.edit_text(updated_text, reply_markup=None, parse_mode="Markdown")

    client_reply = f"✅ **Замовлення прийнято!**\n🚗 **Водій:** {driver_display_name} ({driver_data['car']})\n💰 **Оплата:** {payment_method}"
    if payment_method == 'Картка':
        client_reply += f"\n\n💳 **Картка:**\n`{driver_data['card']}`"

    if client_id != 0:
        await bot.send_message(client_id, client_reply, parse_mode="Markdown")
    await callback.answer("Успішно прийнято!")

async def main():
    import uvicorn
    await bot.delete_webhook(drop_pending_updates=True)
    port = int(os.environ.get("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port)
    server = uvicorn.Server(config)
    await asyncio.gather(dp.start_polling(bot), server.serve())

if __name__ == '__main__':
    asyncio.run(main())
