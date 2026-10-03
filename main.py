import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Ваш новий токен бота
TOKEN = "8895482400:AAF22IJsYMCOImngnkhXfjFml8X0Z5_sG4k"

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    # Посилання на ваш міні-додаток (GitHub Pages)
    web_app_url = "https://maksimshapka-stack.github.io/taxi-app/"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚗 Замовити таксі (Кобеляки)",
                    web_app=WebAppInfo(url=web_app_url)
                )
            ]
        ]
    )
    
    await message.answer(
        "👋 Вітаємо у службі таксі Кобеляки!\n"
        "Натисніть кнопку нижче, щоб відкрити карту та оформити замовлення:",
        reply_markup=keyboard
    )

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
