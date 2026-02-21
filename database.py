import os
import sqlite3
from datetime import datetime

import gspread
import requests
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

SHEET_URL = "https://docs.google.com/spreadsheets/d/1mYOoN2ni9agEdAMogONUw9gn59xqVhaCJwcwkfOasP4/edit"
JSON_KEYITILE = "service_account.json"
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
MANAGER_ART = os.getenv("MANAGER_ART")
MANAGER_ORT = os.getenv("MANAGER_ORT")

managers_str = os.getenv("MANAGER_IDS", "")
MANAGER_IDS = [m_id.strip() for m_id in managers_str.split(",") if m_id.strip()]


def init_db():
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS requests
                   (
                       id       INTEGER PRIMARY KEY AUTOINCREMENT,
                       date     TEXT,
                       platform TEXT,
                       name     TEXT,
                       phone    TEXT,
                       service  TEXT
                   )
                   ''')
    conn.commit()
    conn.close()


init_db()


def send_smart_alert(platform, name, phone, service):
    if not TG_TOKEN:
        print("Ошибка: Нет TG_TOKEN")
        return

    recipients = set()
    if ADMIN_ID:
        recipients.add(ADMIN_ID)

    if service in ["Сейталиев Арт", "Айкидо"]:
        if MANAGER_ART:
            recipients.add(MANAGER_ART)

    elif service in ["ОРТ Vector", "Школьные предметы", "Языки"]:
        if MANAGER_ORT:
            recipients.add(MANAGER_ORT)

    if not recipients:
        print("Нет получателей для уведомления (проверьте .env)")
        return

    text = (
        f"<b>🔔 НОВАЯ ЗАЯВКА!</b>\n\n"
        f"<b>👤 Имя:</b> {name}\n"
        f"<b>📱 Телефон:</b> {phone}\n"
        f"<b>📝 Услуга:</b> {service}\n"
        f"<b>🌐 Источник:</b> {platform}"
    )

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"

    for chat_id in recipients:
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, json=data)
            print(f"Уведомление отправлено пользователю: {chat_id}")
        except Exception as e:
            print(f"Ошибка отправки пользователю {chat_id}: {e}")


def save_data(platform, name, phone, service):
    date_now = datetime.now().strftime("%d.%m.%Y %H:%M")
    week_number = datetime.now().isocalendar()[1]
    week_str = f"Неделя {week_number}"

    sqlite_data = (date_now, platform, name, phone, service)

    gsheets_data = [date_now, week_str, platform, name, phone, service]

    try:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO requests (date, platform, name, phone, service) VALUES (?, ?, ?, ?, ?)",
                       sqlite_data)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка БД: {e}")

    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYITILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SHEET_URL).sheet1
        sheet.append_row(gsheets_data)
        print(f"[{platform}] Сохранено в Google Sheets")
    except Exception as e:
        print(f"Ошибка Google Sheets: {e}")

    send_smart_alert(platform, name, phone, service)
