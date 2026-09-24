import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

TOKEN = "8895482400:AAECLb1186EcGMi5laXwO3DYWayckFJ-dIk"
DRIVERS_CHAT_ID = -1002456789123  # Замініть на ID вашої групи водіїв або свій ID для тестів

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Стани для оформлення замовлення
class OrderState(StatesGroup):
    waiting_for_from = State()
    waiting_for_to = State()

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚖 Замовити таксі")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "👋 Вітаємо у службі таксі Кобеляки!\n\n"
        "Натисніть кнопку нижче, щоб розпочати замовлення:",
        reply_markup=keyboard
    )

@dp.message(F.text == "🚖 Замовити таксі")
async def start_order(message: Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Центр"), KeyboardButton(text="📍 Автостанція")],
            [KeyboardButton(text="📍 Вокзал"), KeyboardButton(text="📍 Лікарня")]
        ],
        resize_keyboard=True
    )
    await message.answer("Звідки вас забрати? (Оберіть із меню або введіть свою адресу):", reply_markup=keyboard)
    await state.set_state(OrderState.waiting_for_from)

@dp.message(OrderState.waiting_for_from)
async def process_from(message: Message, state: FSMContext):
    await state.update_data(address_from=message.text)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏁 АТБ"), KeyboardButton(text="🏁 Центр")],
            [KeyboardButton(text="🏁 Покровська 50"), KeyboardButton(text="❌ Скасувати")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"📍 Звідки: <b>{message.text}</b>\n\nКуди їдемо (пункт призначення)?", parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(OrderState.waiting_for_to)

@dp.message(OrderState.waiting_for_to)
async def process_to(message: Message, state: FSMContext):
    if message.text == "❌ Скасувати":
        await state.clear()
        await command_start_handler(message, state)
        return

    data = await state.get_data()
    address_from = data.get("address_from")
    address_to = message.text

    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"

    # Сповіщення клієнту
    await message.answer(
        f"✅ **Ваше замовлення прийняте!**\n\n"
        f"📍 Звідки: {address_from}\n"
        f"🏁 Куди: {address_to}\n\n"
        f"⏳ Шукаємо вільного водія...",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

    # Кнопки для водіїв
    drivers_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Прийняти", callback_data=f"accept_{user_id}"),
                InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_{user_id}")
            ]
        ]
    )

    driver_text = (
        f"🚨 **НОВЕ ЗАМОВЛЕННЯ!**\n\n"
        f"👤 **Клієнт:** {user_name} ({user_username})\n"
        f"📍 **Звідки:** {address_from}\n"
        f"🏁 **Куди:** {address_to}"
    )

    # Надсилаємо у чат водіїв
    try:
        await bot.send_message(
            chat_id=DRIVERS_CHAT_ID,
            text=driver_text,
            reply_markup=drivers_keyboard,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.error(f"Помилка відправки водіям: {e}")

    await state.clear()

# Обробка кнопок водіїв
@dp.callback_query(F.data.startswith("accept_") | F.data.startswith("reject_"))
async def driver_action_handler(callback: CallbackQuery):
    action, client_id_str = callback.data.split("_")
    client_id = int(client_id_str)
    driver_name = callback.from_user.full_name

    if action == "accept":
        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            f"✅ **Замовлення прийняв водій:** {driver_name}",
            parse_mode="Markdown"
        )
        try:
            await bot.send_message(
                chat_id=client_id,
                text=f"🎉 **Ваш водій знайшовся!**\n🚗 Водій *{driver_name}* прийняв замовлення та вже їде до вас!",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await callback.answer("Ви успішно прийняли замовлення!")

    elif action == "reject":
        await callback.message.edit_text(
            f"{callback.message.text}\n\n"
            f"❌ **Замовлення відхилено водієм ({driver_name})**",
            parse_mode="Markdown"
        )
        await callback.answer("Ви відхилили замовлення.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
