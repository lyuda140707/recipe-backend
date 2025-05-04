from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from telegram_bot import bot, dp
from aiogram.types import Update
import asyncio
from fastapi import FastAPI
from wayforpay import generate_wayforpay_payment




# Читання credentials із Secret File
with open('/etc/secrets/credentials.json', 'r') as f:
    credentials_info = json.load(f)

credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])

# Підключення до Google Sheets
client = gspread.authorize(credentials)
spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1zJOrLr_uNCL0_F7Qcrgwg_K0YCSEy9ISoWX_ZUDuSYg/edit')
worksheet = spreadsheet.sheet1

# Створення FastAPI
app = FastAPI()

@app.get("/create-payment")
def create_payment(user_id: int):
    payment_data = generate_wayforpay_payment(user_id)
    return payment_data
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
    
# Завантажити всі рецепти
def load_all_recipes():
    return worksheet.get_all_records()

import re  # або перенеси нагору

def clean_category(raw: str):
    # видаляє всі емодзі та приводить до нижнього регістру
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

    
from collections import defaultdict
import random

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


@app.get("/ping")
async def ping():
    return {"pong": True}


from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

class PaymentNotification(BaseModel):
    name: str
    user_id: int
    username: str

@app.post("/notify-payment")
async def notify_payment(data: PaymentNotification):
    message = (
        f"💳 Хтось натиснув 'Я оплатив'\n\n"
        f"👤 Username: @{data.username}\n"
        f"🆔 ID: <code>{data.user_id}</code>\n"
        f"📛 Імʼя/номер картки: <b>{data.name}</b>"
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



