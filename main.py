import os
from datetime import datetime

import gspread
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

app = Flask(__name__)

user_states = {}


def send_message(to_number, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        return response
    except Exception as e:
        print(f"Ошибка отправки: {e}")


def save_to_google_sheets(data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Заявки Бот").sheet1
        sheet.append_row(data)
        print("Данные успешно сохранены в таблицу!")
    except Exception as e:
        print(f"Ошибка сохранения в таблицу (проверь файл json и права доступа): {e}")


def get_bot_response(chat_id, text):
    if not text:
        return "Извините, я понимаю только текст."

    state_data = user_states.get(chat_id, {"step": "START"})
    step = state_data["step"]

    text_clean = text.strip().lower()

    if step == "START":
        user_states[chat_id] = {"step": "ASK_NAME"}
        return ("Вас приветствует Центр Наук и Искусств!\n"
                "Подскажите, как мы можем к вам обращаться? (Введите ваше ФИО)")

    elif step == "ASK_NAME":
        user_states[chat_id].update({"step": "ASK_PHONE", "name": text})
        return f"Приятно познакомиться, {text}! Теперь введите ваш номер телефона для связи."

    elif step == "ASK_PHONE":
        user_states[chat_id].update({"step": "ASK_SERVICE", "phone": text})
        return ("Выберите интересующую услугу (введите цифру):\n"
                "1 — Рисование\n2 — ОРТ\n3 — Языки\n"
                "4 — Предметы\n5 — Айкидо")

    elif step == "ASK_SERVICE":
        services = {"1": "Рисование", "2": "ОРТ", "3": "Языки", "4": "Предметы", "5": "Айкидо"}
        service = services.get(text_clean, "Другое")

        user_data = user_states[chat_id]
        row = [
            datetime.now().strftime("%d.%m.%Y %H:%M"),
            "WhatsApp",
            user_data["name"],
            user_data["phone"],
            service
        ]

        save_to_google_sheets(row)

        user_states[chat_id] = {"step": "START"}
        return "Спасибо! Ваша заявка принята. Менеджер свяжется с вами в ближайшее время."

    return "Чтобы начать заново, напишите 'Привет'."


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Forbidden", 403

    if request.method == "POST":
        data = request.json
        try:
            if data.get("entry") and data["entry"][0].get("changes"):
                value = data["entry"][0]["changes"][0]["value"]

                if "messages" in value:
                    phone_number = value["messages"][0]["from"]
                    message_body = value["messages"][0].get("text", {}).get("body")

                    print(f"Сообщение от {phone_number}: {message_body}")

                    response_text = get_bot_response(phone_number, message_body)

                    send_message(phone_number, response_text)

        except Exception as e:
            print(f"Ошибка обработки: {e}")

        return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
