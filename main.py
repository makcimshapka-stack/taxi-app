@dp.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        from_addr = data.get("address_from", "Не вказано")
        to_addr = data.get("address_to", "Не вказано")
        passenger_name = message.from_user.full_name
        username = message.from_user.username
        passenger_username = f"@{username}" if username else "немає"
        
        # Повідомлення пасажиру
        await message.answer(f"✅ Ваше замовлення прийнято!\n📍 Звідки: {from_addr}\n🏁 Куди: {to_addr}\n\nШукаємо водія...")

        # Клавіатура для водія
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Взяти замовлення", callback_data="accept_order")]
        ])

        driver_text = (
            f"🚨 **НОВЕ ЗАМОВЛЕННЯ ТАКСІ!** 🚨\n\n"
            f"👤 Пасажир: {passenger_name} ({passenger_username})\n"
            f"📍 Звідки: {from_addr}\n"
            f"🏁 Куди: {to_addr}"
        )

        target_chat = DRIVER_CHAT_ID if DRIVER_CHAT_ID != "same" else message.chat.id
        await bot.send_message(target_chat, driver_text, reply_markup=kb, parse_mode="Markdown")

    except Exception as e:
        await message.answer("Сталася помилка при обробці замовлення.")
