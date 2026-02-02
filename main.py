import os

from dotenv import load_dotenv
from whatsapp_api_client_python import API

load_dotenv()
greenPortal = API.GreenApi(os.getenv("ID_INSTANCE"), os.getenv("API_TOKEN"))

user_states = {}


def get_bot_response(chat_id, text):
    text = text.lower().strip()
    state = user_states.get(chat_id, "START")

    if state == "START":
        user_states[chat_id] = "ASK_CATEGORY"
        return ("Добрый день! Центр Сейталиев Арт / Центр наук и искусств. "
                "Подскажите, пожалуйста, какой курс вас интересует: рисование, ОРТ или языковые курсы?")

    if state == "ASK_CATEGORY":
        user_states[chat_id] = "ASK_AGE"
        return "Подскажите, пожалуйста, вы ищете курс для ребёнка или для взрослого? У нас есть разные программы."

    if state == "ASK_AGE":
        user_states[chat_id] = "OFFER_TRIAL"
        info = ("У нас работают профессиональные художники с академическим образованием и большим опытом. "
                "Мы предлагаем академический рисунок, живопись и эстетические курсы для развития вкуса. ")
        invitation = "Вы можете подойти в нашу студию, посмотреть обстановку и пройти пробное занятие. Когда вам было бы удобно?"
        return f"{info}\n\n{invitation}"

    if state == "OFFER_TRIAL":
        user_states[chat_id] = "START"
        return "Отлично! Я передаю ваш контакт старшему администратору, он свяжется с вами для подтверждения времени."

    return "Подскажите, пожалуйста, какой курс вас интересует?"


def main():
    print("Бот-менеджер запущен...")
    while True:
        receive_result = greenPortal.receiving.receiveNotification()
        if receive_result.data:
            notification = receive_result.data
            body = notification.get("body", {})

            if body.get("typeWebhook") in ["incomingMessageReceived", "incomingBusinessMessageReceived"]:
                chat_id = body.get("senderData", {}).get("chatId")
                text = body.get("messageData", {}).get("textMessageData", {}).get("textMessage") or \
                       body.get("messageData", {}).get("extendedTextMessageData", {}).get("text")

                if text:
                    print(f"Клиент {chat_id}: {text}")
                    answer = get_bot_response(chat_id, text)
                    greenPortal.sending.sendMessage(chat_id, answer)

            greenPortal.receiving.deleteNotification(notification.get("receiptId"))


if __name__ == "__main__":
    main()