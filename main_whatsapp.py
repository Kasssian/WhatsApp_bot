import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

from ai_handler import get_ai_response
from database import save_data

load_dotenv()
app = Flask(__name__)

ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN")


def send_message(chat_id, text):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": chat_id,
        "message": text
    }
    headers = {'Content-Type': 'application/json'}
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Ошибка отправки WhatsApp: {e}")


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json

        try:
            if data['typeWebhook'] == 'incomingMessageReceived':
                message_data = data['messageData']

                if message_data['typeMessage'] == 'textMessage':
                    chat_id = data['senderData']['chatId']  # Например: 996555123456@c.us
                    text = message_data['textMessageData']['textMessage']

                    if chat_id == data['idInstance']:
                        return jsonify({"status": "ignored"}), 200

                    ai_reply = get_ai_response(chat_id, text)

                    if "||ЗАЯВКА:" in ai_reply:
                        try:
                            secret_line = ai_reply.split("||ЗАЯВКА:")[1].split("||")[0].strip()
                            data_parts = secret_line.split(",")
                            name = data_parts[0].strip()
                            # Номер берем из chat_id (отрезаем @c.us в конце)
                            phone = chat_id.split('@')[0]
                            service = data_parts[2].strip()

                            save_data("WhatsApp", name, phone, service)

                            # Вырезаем секретный код из текста
                            ai_reply = ai_reply.split("||ЗАЯВКА:")[0].strip()
                        except Exception as e:
                            print(f"Ошибка парсинга заявки WA: {e}")

                    send_message(chat_id, ai_reply)

        except KeyError:
            pass

    except Exception as e:
        print(f"Критическая ошибка вебхука: {e}")

    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    print("----- WhatsApp GREEN-API бот запущен... -----")
    app.run(host='0.0.0.0', port=5000)
