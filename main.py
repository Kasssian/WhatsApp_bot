import os
import sqlite3
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1mYOoN2ni9agEdAMogONUw9gn59xqVhaCJwcwkfOasP4/edit"

app = Flask(__name__)
user_states = {}


def init_db():
    conn = sqlite3.connect('bot_database.db')
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
    print("База данных SQLite подключена и проверена.")


init_db()


def save_to_sqlite(data_list):
    try:
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO requests (date, platform, name, phone, service) VALUES (?, ?, ?, ?, ?)", data_list)
        conn.commit()
        conn.close()
        print("Сохранено в локальную БД")
    except Exception as e:
        print(f"Ошибка локальной БД: {e}")


def save_to_google_sheets(data_list):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        client = gspread.authorize(creds)
        sheet_url = "https://docs.google.com/spreadsheets/d/1mYOoN2ni9agEdAMogONUw9gn59xqVhaCJwcwkfOasP4/edit"
        sheet = client.open_by_url(sheet_url).sheet1
        sheet.append_row(data_list)
        print("Сохранено в Google Таблицу")
    except Exception as e:
        print(f"Ошибка Google Sheets: {e}")


def send_message(to_number, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        print(f"ОШИБКА ОТПРАВКИ: {response.text}")
    else:
        print(f"Ответ отправлен: {text}")


def get_bot_response(chat_id, text):
    if not text: return "Пришлите текст."

    state_data = user_states.get(chat_id, {"step": "START"})
    step = state_data["step"]
    text = text.strip()

    if step == "START":
        user_states[chat_id] = {"step": "ASK_NAME"}
        return "Вас приветствует Центр! Как к вам обращаться? (ФИО)"

    elif step == "ASK_NAME":
        user_states[chat_id].update({"step": "ASK_PHONE", "name": text})
        return f"Приятно познакомиться, {text}! Введите ваш номер телефона."

    elif step == "ASK_PHONE":
        user_states[chat_id].update({"step": "ASK_SERVICE", "phone": text})
        return "Выберите услугу (цифру):\n1 — Рисование\n2 — ОРТ\n3 — Языки\n4 — Предметы\n5 — Айкидо"

    elif step == "ASK_SERVICE":
        services = {"1": "Рисование", "2": "ОРТ", "3": "Языки", "4": "Предметы", "5": "Айкидо"}
        service_name = services.get(text, "Другое")

        user_data = user_states[chat_id]

        row_data = [
            datetime.now().strftime("%d.%m.%Y %H:%M"),  # Дата
            "WhatsApp",
            user_data["name"],
            user_data["phone"],
            service_name
        ]

        save_to_sqlite(row_data)
        save_to_google_sheets(row_data)

        user_states[chat_id] = {"step": "START"}
        return "Ваша заявка принята и сохранена! Менеджер скоро свяжется."

    return "Напишите 'Привет' для начала."


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Forbidden", 403

    if request.method == "POST":
        data = request.json
        try:
            if data.get("entry"):
                changes = data["entry"][0]["changes"][0]["value"]
                if "messages" in changes:
                    phone = changes["messages"][0]["from"]
                    msg_body = changes["messages"][0]["text"]["body"]

                    print(f"Сообщение от {phone}: {msg_body}")
                    reply = get_bot_response(phone, msg_body)
                    send_message(phone, reply)
        except Exception as e:
            print(f"Ошибка: {e}")
        return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)