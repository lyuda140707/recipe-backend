from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import threading
from telegram_bot import run_bot  # імпортуємо запуск бота

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Завантажити всі рецепти
def load_all_recipes():
    return worksheet.get_all_records()

@app.get("/recipes")
async def get_recipes(request: Request):
    all_recipes = load_all_recipes()
    category = request.query_params.get("category")

    if category:
        return [r for r in all_recipes if r.get("Категорія", "").strip().lower() == category.strip().lower()]
    return all_recipes

# Запустити Telegram-бота у фоновому потоці
threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
