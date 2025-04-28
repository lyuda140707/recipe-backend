import os
import json
from io import StringIO
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Читання credentials із змінної середовища
credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])

client = gspread.authorize(credentials)

# Відкриття таблиці
spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1zJOrLr_uNCL0_F7Qcrgwg_K0YCSEy9ISoWX_ZUDuSYg/edit')
worksheet = spreadsheet.sheet1

# Додаток FastAPI
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Завантажити всі рецепти
def load_all_recipes():
    data = worksheet.get_all_records()
    return data

# Ендпоінт
@app.get("/recipes")
async def get_recipes(request: Request):
    all_recipes = load_all_recipes()
    category = request.query_params.get('category')

    if category:
        filtered = [
            r for r in all_recipes
            if r.get("Категорія", "").strip().lower() == category.strip().lower()
        ]
        return filtered

    return all_recipes

# Локальний запуск
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
