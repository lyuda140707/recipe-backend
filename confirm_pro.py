import os
import asyncio
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

async def activate_pro(user_id):
    try:
        await bot.send_message(chat_id=user_id, text="✅ PRO доступ активовано! Насолоджуйтесь усіма функціями 💛")
    except Exception as e:
        print(f"Помилка при надсиланні повідомлення: {e}")

if __name__ == "__main__":
    user_id = input("Введи Telegram ID користувача, якому активувати PRO: ")
    asyncio.run(activate_pro(user_id))
