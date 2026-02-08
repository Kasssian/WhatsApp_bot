import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

from database import save_data

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

users = {}


def send_message(to_number, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": text}
    }
    requests.post(url, json=data, headers=headers)


def process_message(chat_id, text):
    state = users.get(chat_id, {"step": "START"})
    step = state["step"]

    if step == "START":
        users[chat_id] = {"step": "ASK_NAME"}
        return "Вас приветствует Центр! Как к вам обращаться? (ФИО)"

    elif step == "ASK_NAME":
        users[chat_id].update({"step": "ASK_PHONE", "name": text})
        return f"Приятно познакомиться, {text}! Введите номер телефона."

    elif step == "ASK_PHONE":
        users[chat_id].update({"step": "ASK_SERVICE", "phone": text})
        return "Выберите услугу (цифру):\n1 — Рисование\n2 — ОРТ\n3 — Языки\n4 — Предметы\n5 — Айкидо"

    elif step == "ASK_SERVICE":
        services = {"1": "Рисование", "2": "ОРТ", "3": "Языки", "4": "Предметы", "5": "Айкидо"}
        service_name = services.get(text, text)

        user_data = users[chat_id]
        save_data("WhatsApp", user_data['name'], user_data['phone'], service_name)

        users[chat_id] = {"step": "START"}
        return "Заявка сохранена! Менеджер свяжется с вами."

    return "Напишите Привет."


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
                    msg = changes["messages"][0]["text"]["body"]
                    reply = process_message(phone, msg)
                    send_message(phone, reply)
        except:
            pass
        return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    print("----- WhatsApp сервер запущен... -----")
    app.run(port=5000)
