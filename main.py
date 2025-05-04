from aiohttp import web
import os
import asyncio
from aiogram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

bot = Bot(token=BOT_TOKEN)

routes = web.RouteTableDef()

@routes.post("/notify-payment")
async def notify_payment(request):
    data = await request.json()
    name = data.get("name")
    user_id = data.get("user_id")
    username = data.get("username", "невідомо")

    text = f"💸 Оплата!\n👤 {name}\n🆔 {user_id}\n🔗 @{username}"
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
    return web.json_response({"status": "ok"})

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("PORT", 8080)))
