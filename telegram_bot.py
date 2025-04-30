from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils import executor
import os

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
Bot.set_current(bot)  # ВАЖЛИВО!
dp = Dispatcher(bot)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Відкрити меню", web_app=WebAppInfo(url="https://lyuda140707.github.io/telegram-recipe-webapp/"))]
    ])
    await message.answer("Привіт! 👋 Щоб почати — натисни кнопку нижче 👇", reply_markup=keyboard)
 
