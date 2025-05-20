from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command  # тільки один раз
import os
from pro_utils import add_pro_user
from aiogram import types


API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
Bot.set_current(bot)  # ВАЖЛИВО!
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    print("🔐 Твій Telegram ID:", message.chat.id)
    await message.answer(f"Ваш Telegram ID: <code>{message.chat.id}</code>", parse_mode="HTML")



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

from aiogram import types

@dp.channel_post_handler()
async def handle_any_channel_post(post: types.Message):
    admin_id = int(os.getenv("ADMIN_CHAT_ID"))

    if post.video:
        file_id = post.video.file_id
        print(f"🎯 Знайдено відео, file_id: {file_id}")  # ➕ ДОДАЙ ЦЕ

        try:
            await bot.send_message(
                admin_id,
                f"🎥 Відео з каналу. file_id:\n<code>{file_id}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            print("❌ Помилка надсилання відео file_id:", e)

    try:
        post_summary = f"Повідомлення:\n{post.caption or '(без тексту)'}"
        print(f"📝 {post_summary}")  # ➕ ДОДАЙ ЦЕ

        await bot.send_message(
            admin_id,
            f"📣 Повне повідомлення:\n<code>{post}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        print("❌ Помилка надсилання повного поста:", e)





