import os
from datetime import datetime

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from whatsapp_api_client_python import API

load_dotenv()

ID_INSTANCE = os.getenv("ID_INSTANCE")
API_TOKEN = os.getenv("API_TOKEN")

greenPortal = API.GreenApi(ID_INSTANCE, API_TOKEN)
user_states = {}


def save_to_google_sheets(data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Заявки Бот").sheet1
        sheet.append_row(data)
    except Exception as e:
        print(f"Ошибка сохранения в таблицу: {e}")


def get_bot_response(chat_id, text):
    state_data = user_states.get(chat_id, {"step": "START"})
    step = state_data["step"]
    text_lower = text.strip().lower()

    if step == "START":
        user_states[chat_id] = {"step": "ASK_NAME"}
        return ("Вас приветствует Центр Наук и Искусств!\n"
                "Подскажите, как мы можем к вам обращаться? (Введите ваше ФИО) ")

    elif step == "ASK_NAME":
        user_states[chat_id].update({"step": "ASK_PHONE", "name": text})
        return f"Приятно познакомиться, {text}! Теперь введите ваш номер телефона для связи. "

    elif step == "ASK_PHONE":
        user_states[chat_id].update({"step": "ASK_SERVICE", "phone": text})
        return ("Выберите интересующую услугу (введите цифру):\n"
                "1 — Рисование\n2 — ОРТ\n3 — Языки\n"
                "4 — Предметы\n5 — Айкидо")

    elif step == "ASK_SERVICE":
        services = {"1": "Рисование", "2": "ОРТ", "3": "Языки", "4": "Предметы", "5": "Айкидо"}
        service = services.get(text, "Другое")

        user_data = user_states[chat_id]
        row = [
            datetime.now().strftime("%d.%m.%Y %H:%M"),  # Дата
            "WhatsApp",
            user_data["name"],
            user_data["phone"],
            service
        ]
        save_to_google_sheets(row)

        user_states[chat_id] = {"step": "START"}
        return "Спасибо! Ваша заявка принята. Менеджер свяжется с вами в ближайшее время."

    return "Пожалуйста, следуйте инструкциям бота."


def main():
    print("Бот-Центр запущен...")
    while True:
        receive_result = greenPortal.receiving.receiveNotification()
        if receive_result.data:
            notification = receive_result.data
            body = notification.get("body", {})

            if body.get("typeWebhook") in ["incomingMessageReceived", "incomingBusinessMessageReceived"]:
                chat_id = body.get("senderData", {}).get("chatId")
                message_data = body.get("messageData", {})
                text = (message_data.get("textMessageData", {}).get("textMessage") or
                        message_data.get("extendedTextMessageData", {}).get("text"))

                if text:
                    print(f"Запрос от {chat_id}: {text}")
                    response = get_bot_response(chat_id, text)
                    greenPortal.sending.sendMessage(chat_id, response)

            greenPortal.receiving.deleteNotification(notification.get("receiptId"))


if __name__ == "__main__":
    main()
