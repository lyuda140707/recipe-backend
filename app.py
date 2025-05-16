from fastapi import FastAPI, Request
import requests
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import json
import gspread
import httpx
import random
import re
from collections import defaultdict
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from telegram_bot import bot, dp
from aiogram.types import Update
from wayforpay import generate_wayforpay_payment


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

    

# Ініціалізація FastAPI
app = FastAPI()

# Додаємо CORS — обовʼязково для WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можеш вказати точний домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Дозволити всі CORS-запити
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Авторизація з Google Sheets
with open('/etc/secrets/credentials.json', 'r') as f:
    credentials_info = json.load(f)

credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(credentials)
spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1zJOrLr_uNCL0_F7Qcrgwg_K0YCSEy9ISoWX_ZUDuSYg/edit')
worksheet = spreadsheet.sheet1




# Webhook Telegram
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook("https://recipe-backend-0gz1.onrender.com/webhook")
    print("✅ Webhook встановлено")


@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    telegram_update = Update(**data)
    print("✅ Я оновлений!")
    await dp.process_update(telegram_update)
    return {"ok": True}

# Ендпоінт створення платежу
@app.get("/create-payment")
def create_payment(user_id: int):
    payment_data = generate_wayforpay_payment(user_id)
    return payment_data

# Пінг
@app.get("/ping")
async def ping():
    return {"pong": True}

# Завантаження всіх рецептів
def load_all_recipes():
    return worksheet.get_all_records()

def clean_category(raw: str):
    return re.sub(r'[^\w\s]', '', raw).strip().lower()

@app.get("/recipes")
async def get_recipes(request: Request):
    all_recipes = load_all_recipes()
    category = request.query_params.get("category")

    if category:
        clean_input = clean_category(category)
        return [
            r for r in all_recipes
            if clean_category(r.get("категорія", "")) == clean_input
        ]
    return all_recipes

@app.get("/weekly-menu")
async def generate_weekly_menu():
    categories = {
        "Пн": "🥘 Другі страви",
        "Вт": "🥪 Закуски",
        "Ср": "🍞 Випічка",
        "Чт": "🍲 Перші страви",
        "Пт": "🍰 Десерти",
        "Сб": "🥤 Напої",
        "Нд": "🥗 Салати"
    }

    data = load_all_recipes()
    menu = {}

    for day, category in categories.items():
        filtered = [row for row in data if clean_category(row.get("категорія", "")) == clean_category(category)]
        grouped = defaultdict(list)
        for row in filtered:
            grouped[row["номер рецепту"]].append(row)

        if grouped:
            chosen_number = random.choice(list(grouped.keys()))
            menu[day] = grouped[chosen_number]
        else:
            menu[day] = []

    return menu

# Повідомлення про оплату (кнопка "Я оплатив")
class PaymentNotification(BaseModel):
    name: str
    user_id: int
    username: str

@app.post("/notify-payment")
async def notify_payment(data: PaymentNotification):
    print("✅ Запит прийнято:", data.dict())

    message = (
        f"🧾 Запит на PRO доступ\n"
        f"👤 Імʼя/картка: <b>{data.name}</b>\n"
        f"🆔 ID: <code>{data.user_id}</code>\n"
        f"📛 Username: @{data.username or 'немає'}\n\n"
        f"👉 /ok {data.user_id}"
    )

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": ADMIN_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
        )

    return {"status": "ok"}
from pro_utils import is_pro_user  # Додай імпорт

    




@app.get("/is-pro")
async def check_pro(request: Request):
    user_id = request.query_params.get("user_id")
    if not user_id:
        return {"is_pro": False}
    return is_pro_user(user_id)

@app.get("/check-subscription")
async def check_subscription(user_id: int):
    if not user_id:
        return {"is_subscribed": False}

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {
        "chat_id": CHANNEL_USERNAME,
        "user_id": user_id
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    print(f"🔍 Результат перевірки підписки: {data}")

    if data.get("ok") and data.get("result", {}).get("status") in ["member", "administrator", "creator"]:
        return {"is_subscribed": True}
    else:
        return {"is_subscribed": False}

@app.get("/send-webapp-button")
async def send_webapp_button():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_USERNAME,
        "text": "🎉 Дякуємо за підписку! Тисни нижче, щоб повернутись у застосунок 👇",
        "reply_markup": {
            "inline_keyboard": [[
                {
                    "text": "🍳 Відкрити WebApp",
                    "web_app": {
                        "url": os.getenv("WEBAPP_URL")
                    }
                }
            ]]
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        print("✅ Відправлено в канал:", response.json())
        return response.json()
