import os

from dotenv import load_dotenv
from whatsapp_api_client_python import API

load_dotenv()
ID_INSTANCE = os.getenv("ID_INSTANCE")
API_TOKEN = os.getenv("API_TOKEN")

greenPortal = API.GreenApi(ID_INSTANCE, API_TOKEN)


def main():
    if not ID_INSTANCE or not API_TOKEN:
        print("Ошибка: Ключи не найдены в файле .env!")
        return

    print(f"Бот запущен с ID: {ID_INSTANCE}")
    print("Бот запущен и ожидает сообщений...")

    while True:
        receive_result = greenPortal.receiving.receiveNotification()

        if receive_result.data:
            notification = receive_result.data
            body = notification.get("body", {})
            type_webhook = body.get("typeWebhook")

            print(f"--- Получено событие типа: {type_webhook} ---")

            incoming_types = [
                "incomingMessageReceived",
                "incomingBusinessMessageReceived",
                "incomingCustomMessageReceived"
            ]

            if type_webhook in incoming_types:
                sender_data = body.get("senderData", {})
                chat_id = sender_data.get("chatId")

                message_data = body.get("messageData", {})

                text_message = (
                        message_data.get("textMessageData", {}).get("textMessage") or
                        message_data.get("extendedTextMessageData", {}).get("text")
                )

                if text_message:
                    print(f"Текст: {text_message} от {chat_id}")

                    if "привет" in text_message.lower():
                        greenPortal.sending.sendMessage(chat_id, "Вижу тебя, бизнес-аккаунт!")
                else:
                    print("Сообщение получено, но текста внутри нет (возможно, картинка или файл)")

            greenPortal.receiving.deleteNotification(notification.get("receiptId"))


if __name__ == "__main__":
    main()
