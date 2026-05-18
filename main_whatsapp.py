import os
import threading
import time

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

from ai_handler import get_ai_response
from database import save_data

load_dotenv()
app = Flask(__name__)

ID_INSTANCE = os.getenv("GREEN_API_ID")
API_TOKEN_INSTANCE = os.getenv("GREEN_API_TOKEN")

muted_chats = {}
last_bot_replies = {}
MUTE_DURATION = 1800


def send_message(chat_id, text):
    url = "http://127.0.0.1:3000/send"
    payload = {"chatId": chat_id, "message": text}
    headers = {'Content-Type': 'application/json'}

    try:
        last_bot_replies[chat_id] = time.time()

        resp = requests.post(url, json=payload, headers=headers)
        print(f"Ответ отправлен в WA (Статус: {resp.status_code})")
    except Exception as e:
        print(f"Ошибка отправки WhatsApp: {e}")


def process_and_send(chat_id, text):
    print(f"Текст от клиента {chat_id}: {text}")
    ai_reply = get_ai_response(chat_id, text)

    if "||ЗАЯВКА:" in ai_reply:
        try:
            secret_line = ai_reply.split("||ЗАЯВКА:")[1].split("||")[0].strip()
            data_parts = secret_line.split(",")
            name = data_parts[0].strip()
            phone = chat_id.split('@')[0]
            service = data_parts[2].strip()

            save_data("WhatsApp", name, phone, service)
            print(f"✅ Заявка сохранена в базу: {name}")

            ai_reply = ai_reply.split("||ЗАЯВКА:")[0].strip()
        except Exception as e:
            print(f"❌ Ошибка парсинга заявки WA: {e}")

    send_message(chat_id, ai_reply)


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "ok"}), 200

        type_webhook = data.get('typeWebhook')
        print(f"\n[ВЕБХУК] 📥 Новое событие: {type_webhook}")

        if type_webhook == 'outgoingMessageReceived':
            chat_id = data.get('senderData', {}).get('chatId')
            if not chat_id: return jsonify({"status": "ok"}), 200

            now = time.time()
            last_reply = last_bot_replies.get(chat_id, 0)

            if now - last_reply < 5:
                print(f"[ВЕБХУК] 🤖 Это мой собственный ответ в {chat_id}. Не мутим.")
                return jsonify({"status": "ignored_self_reply"}), 200

            muted_chats[chat_id] = now
            print(f"[ВЕБХУК] 🤫 Обнаружен ответ МЕНЕДЖЕРА. Чат {chat_id} замолчит на 30 минут.")
            return jsonify({"status": "muted"}), 200

        if type_webhook == 'incomingMessageReceived':
            chat_id = data.get('senderData', {}).get('chatId')
            message_data = data.get('messageData', {})
            type_message = message_data.get('typeMessage')

            if chat_id in muted_chats:
                time_passed = time.time() - muted_chats[chat_id]
                if time_passed > MUTE_DURATION:
                    del muted_chats[chat_id]
                    print(f"[ВЕБХУК] ✅ Время тишины для {chat_id} истекло.")
                else:
                    remaining = int(MUTE_DURATION - time_passed)
                    print(f"[ВЕБХУК] 🙊 Бот промолчал: {chat_id} в списке тишины (еще {remaining} сек.)")
                    return jsonify({"status": "ignored_due_to_mute"}), 200

            text = ""
            if type_message == 'textMessage':
                text = message_data.get('textMessageData', {}).get('textMessage', '')
            elif type_message == 'extendedTextMessage':
                text = message_data.get('extendedTextMessageData', {}).get('text', '')

            if text:
                print(f"[ВЕБХУК] 📨 Сообщение от {chat_id}: {text}")

                if chat_id == data.get('idInstance'):
                    return jsonify({"status": "ignored_self"}), 200

                print(f"[ВЕБХУК] ⚙️ Запускаю поток обработки для {chat_id}...")
                thread = threading.Thread(target=process_and_send, args=(chat_id, text))
                thread.start()
            else:
                print(f"[ВЕБХУК] 🖼️ Нетекстовое сообщение от {chat_id}. Игнорирую.")

    except Exception as e:
        print(f"❌ [ОШИБКА ВЕБХУКА]: {e}")

    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    print("----- WhatsApp GREEN-API бот запущен... -----")
    app.run(host='0.0.0.0', port=5000)
