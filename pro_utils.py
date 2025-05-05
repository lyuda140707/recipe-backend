import gspread
import json
import os
from datetime import datetime, timedelta

from oauth2client.service_account import ServiceAccountCredentials

# Завантаження credentials
with open('/etc/secrets/credentials.json', 'r') as f:
    credentials_info = json.load(f)

credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(credentials)
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1zJOrLr_uNCL0_F7Qcrgwg_K0YCSEy9ISoWX_ZUDuSYg/edit")
pro_worksheet = spreadsheet.worksheet("pro_users")

def find_first_empty_row(worksheet):
    rows = worksheet.get_all_values()
    for i, row in enumerate(rows, start=1):
        if not any(cell.strip() for cell in row):  # якщо всі клітинки в рядку пусті
            return i
    return len(rows) + 1  # якщо всі рядки зайняті, вставляємо після останнього




def add_pro_user(user_id: int, username: str, name: str):
    now = datetime.now()
    expires = now + timedelta(days=30)  # додаємо 30 днів
    row = [
        str(user_id),
        username or "",      # захист від None
        name,
        now.strftime("%Y-%m-%d %H:%M:%S"),
        expires.strftime("%Y-%m-%d")     # додаємо дату завершення
    ]
    row_index = find_first_empty_row(pro_worksheet)
    pro_worksheet.update(f"A{row_index}:E{row_index}", [row])  # E замість D





def is_pro_user(user_id: int) -> dict:
    try:
        all_rows = pro_worksheet.get_all_records()
        for row in all_rows:
            row_id = str(row.get("ID Користувача", "")).strip()
            if row_id == str(user_id).strip():
                expires_str = row.get("Дата завершення", "").strip()
                try:
                    expires_date = datetime.strptime(expires_str, "%Y-%m-%d").date()
                    today = datetime.today().date()
                    if expires_date >= today:
                        return {"is_pro": True, "expires": expires_str}
                    else:
                        return {"is_pro": False, "expires": expires_str}  # строка є, але доступ не дійсний
                except ValueError:
                    return {"is_pro": True, "expires": expires_str}  # fallback якщо щось не так з датою
        return {"is_pro": False}
    except Exception as e:
        print(f"❌ Помилка перевірки PRO: {e}")
        return {"is_pro": False}

