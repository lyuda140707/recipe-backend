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

def add_pro_user(user_id: int, username: str, name: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pro_worksheet.append_row([str(user_id), username or "", name, now])


def is_pro_user(user_id: int) -> bool:
    try:
        all_rows = pro_worksheet.get_all_records()
        return any(str(row["ID Користувача"]) == str(user_id) for row in all_rows)
    except Exception as e:
        print(f"❌ Помилка перевірки PRO: {e}")
        return False
