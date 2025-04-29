from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.executor import start_polling
import os

API_TOKEN = os.getenv("BOT_TOKEN")  # має бути додано в Render → Environment

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Відкрити меню", web_app=WebAppInfo(url="https://lyuda140707.github.io/telegram-recipe-webapp/"))]
    ])
    await message.answer("Привіт! 👋 Щоб почати — натисни кнопку нижче 👇", reply_markup=keyboard)

def run_bot():
    start_polling(dp, skip_updates=True)
