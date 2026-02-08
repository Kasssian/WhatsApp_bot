import sqlite3
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_URL = "https://docs.google.com/spreadsheets/d/1mYOoN2ni9agEdAMogONUw9gn59xqVhaCJwcwkfOasP4/edit"
JSON_KEYITILE = "service_account.json"


def init_db():
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS requests
                   (
                       id
                           INTEGER
                           PRIMARY
                               KEY
                           AUTOINCREMENT,
                       date
                           TEXT,
                       platform
                           TEXT,
                       name
                           TEXT,
                       phone
                           TEXT,
                       service
                           TEXT
                   )
                   ''')
    conn.commit()
    conn.close()


init_db()


def save_data(platform, name, phone, service):
    date_now = datetime.now().strftime("%d.%m.%Y %H:%M")
    row_data = [date_now, platform, name, phone, service]

    try:
        conn = sqlite3.connect('bot_database.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO requests (date, platform, name, phone, service) VALUES (?, ?, ?, ?, ?)", row_data)
        conn.commit()
        conn.close()
        print(f"----- [{platform}] Сохранено в БД: {name} -----")
    except Exception as e:
        print(f"----- Ошибка БД: {e} -----")

    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYITILE, scope)
        client = gspread.authorize(creds)

        sheet = client.open_by_url(SHEET_URL).sheet1
        sheet.append_row(row_data)
        print(f"✅ [{platform}] Сохранено в Google Sheets")
    except Exception as e:
        print(f"❌ Ошибка Google Sheets: {e}")
