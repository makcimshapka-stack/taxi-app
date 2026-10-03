import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, types

API_TOKEN = '8895482400:AAH52phykj637HPNBycVjD4ZxFKGZAuhp04'
DRIVER_CHAT_ID = -5357703122

DRIVERS_INFO = {
    "Макс": {
        "card": "4874070013052004",
        "car": "Chery Amulet (КЕ3389АК)",
        "display": "Макс"
    },
    "Артур": {
        "card": "4441114417805692",
        "car": "Renault",
        "display": "Артур"
    },
    "Artut": {
        "card": "4441114417805692",
        "car": "Renault",
        "display": "Артур"
    },
    "Троценко": {
        "card": "4149629378242937",
        "car": "Лада Гранта",
        "display": "Троценко"
    },
    "Валерій": {
        "card": "4149629378242937",
        "car": "Лада Гранта",
        "display": "Валерій"
    }
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(lambda message: message.text and message.text.startswith('/start'))
async def send_welcome(message: types.Message):
    await message.answer(
        "👋 Вітаємо у службі таксі Кобеляки!\n\nДля оформлення замовлення натисніть кнопку **«Замовити таксі»** внизу екрана.",
        parse_mode="Markdown"
    )

@dp.message(lambda message: message.web_app_data is not None)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        address_from = data.get('address_from', 'Не вказано')
        address_to = data.get('address_to', 'Не вказано')
        phone = data.get('phone', 'Не вказано')
        payment_method = data.get('payment_method', 'Готівка')
        price = data.get('price', 100)
        price_desc = data.get('price_desc', '')

        await message.answer("⏳ **Ваше замовлення прийнято! Шукаємо вільне авто...**", parse_mode="Markdown")

        order_text = (
            f"🚨 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!** 🚨\n\n"
            f"📍 **Звідки:** {address_from}\n"
            f"🏁 **Куди:** {address_to}\n"
            f"📞 **Телефон клієнта:** `{phone}`\n"
            f"💳 **Оплата:** {payment_method}\n"
            f"💰 **Вартість:** {price} грн _{price_desc}_\n"
        )

        callback_data_str = f"accept_{message.from_user.id}_{price}_{payment_method}"

        markup = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🚗 Взяти замовлення", callback_data=callback_data_str)]
            ]
        )

        await bot.send_message(DRIVER_CHAT_ID, order_text, reply_markup=markup, parse_mode="Markdown")
        logging.info("✅ Замовлення успішно відправлено у чат водіїв!")

    except Exception as e:
        logging.error(f"Помилка обробки даних WebApp: {e}")
        await message.answer("❌ Сталася помилка при оформленні замовлення.")

@dp.callback_query(lambda c: c.data and c.data.startswith('accept_'))
async def process_accept(callback: types.CallbackQuery):
    try:
        parts = callback.data.split('_')
        client_id = int(parts[1])
        price = parts[2]
        payment_method = parts[3]
        
        first_name = callback.from_user.first_name or ""
        last_name = callback.from_user.last_name or ""

        driver_data = None
        driver_display_name = first_name

        for key, data in DRIVERS_INFO.items():
            if key.lower() in first_name.lower() or key.lower() in last_name.lower():
                driver_data = data
                driver_display_name = data["display"]
                break
        
        if not driver_data:
            driver_data = {"card": "4149629378242937", "car": "Лада Гранта"}
            driver_display_name = first_name or "Водій"

        card_num = driver_data["card"]
        car_info = driver_data["car"]

        if "✅ **Замовлення прийняв" in callback.message.text:
            await callback.answer("⚠️ Це замовлення вже хтось зайняв!", show_alert=True)
            return

        updated_driver_text = (
            callback.message.text + 
            f"\n\n✅ **Замовлення прийняв(ла): {driver_display_name}**\n"
            f"🚗 **Авто:** {car_info}"
        )
        await callback.message.edit_text(updated_driver_text, reply_markup=None, parse_mode="Markdown")

        client_reply = (
            f"✅ **Ваше замовлення прийнято в роботу!**\n\n"
            f"🚗 **Водій:** {driver_display_name} ({car_info})\n"
            f"💰 **Сума до сплати:** {price} грн ({payment_method})"
        )
        if payment_method == 'Картка':
            client_reply += f"\n\n💳 **Номер картки для оплати ({driver_display_name}):**\n`{card_num}`"

        await bot.send_message(client_id, client_reply, parse_mode="Markdown")
        await callback.answer("Ви успішно прийняли замовлення!")

    except Exception as e:
        logging.error(f"Помилка обробки натискання: {e}")
        await callback.answer("❌ Помилка при прийнятті замовлення.", show_alert=True)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот успішно запущено і готовий до роботи!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
