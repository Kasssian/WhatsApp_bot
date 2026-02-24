from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from ai_handler import get_ai_response
from database import save_data

load_dotenv()
app = Flask(__name__)

WA_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


def send_message(to_number, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"messaging_product": "whatsapp", "to": to_number, "type": "text", "text": {"body": text}}
    requests.post(url, headers=headers, json=data)


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Forbidden", 403

    if request.method == 'POST':
        data = request.json
        try:
            message_info = data['entry'][0]['changes'][0]['value']['messages'][0]
            wa_id = message_info['from']
            text = message_info['text']['body']

            ai_reply = get_ai_response(wa_id, text)

            if "||ЗАЯВКА:" in ai_reply:
                try:
                    secret_line = ai_reply.split("||ЗАЯВКА:")[1].split("||")[0].strip()
                    data_parts = secret_line.split(",")
                    name = data_parts[0].strip()
                    service = data_parts[2].strip()

                    save_data("WhatsApp", name, wa_id, service)

                    ai_reply = ai_reply.split("||ЗАЯВКА:")[0].strip()
                except Exception as e:
                    print(f"Ошибка парсинга заявки WA: {e}")

            send_message(wa_id, ai_reply)

        except KeyError:
            pass
        return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)