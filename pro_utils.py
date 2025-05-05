import gspread
import json
import os
from datetime import datetime
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
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [str(user_id), username if username else "-", name, now]
    row_index = find_first_empty_row(pro_worksheet)
    pro_worksheet.update(f"A{row_index}:D{row_index}", [row])



def is_pro_user(user_id: int) -> bool:
    try:
        all_rows = pro_worksheet.get_all_records()
        print("📋 Всі рядки:", all_rows)  # ← Додано
        for row in all_rows:
            row_id = str(row.get("ID Користувача", "")).strip()
            print(f"🔍 Перевіряю: {row_id} == {user_id}")  # ← Додано
            if row_id == str(user_id).strip():
                return True
        return False
    except Exception as e:
        print(f"❌ Помилка перевірки PRO: {e}")
        return False


