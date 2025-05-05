from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command  # тільки один раз
import os
from pro_utils import add_pro_user


API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
Bot.set_current(bot)  # ВАЖЛИВО!
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Відкрити меню", web_app=WebAppInfo(url="https://lyuda140707.github.io/telegram-recipe-webapp/"))]
    ])
    await message.answer("Привіт! 👋 Щоб почати — натисни кнопку нижче 👇", reply_markup=keyboard)


@dp.message_handler(Command("ok"))
async def approve_pro(message: types.Message):
    if str(message.chat.id) != os.getenv("ADMIN_CHAT_ID"):
        await message.reply("⛔ Тобі не дозволено це робити.")
        return

    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("❌ Вкажи ID користувача після /ok")
            return

        user_id = int(args[1])
        username = None
        name = "Оплата підтверджена вручну"

        add_pro_user(user_id, username or "", name)
        await message.reply(f"✅ PRO доступ активовано для ID {user_id}")
        await bot.send_message(user_id, "🎉 Твій PRO доступ активовано! Дякуємо за підтримку!")

    except Exception as e:
        await message.reply(f"❌ Помилка: {e}")
