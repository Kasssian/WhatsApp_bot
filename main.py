import os

from dotenv import load_dotenv
from whatsapp_api_client_python import API

load_dotenv()
greenPortal = API.GreenApi(os.getenv("ID_INSTANCE"), os.getenv("API_TOKEN"))

user_states = {}


def get_main_menu():
    return (
        "Вас приветствует Центр Наук и Искусств!\n"
        "Выберите, пожалуйста, интересующее направление (введите цифру):\n"
        "1 — Рисование, живопись, мастер-классы\n"
        "2 — Подготовка к ОРТ\n"
        "3 — Языковые курсы (English, Deutsch, и др.)\n"
        "4 — Математика, физика, биология, химия\n"
        "5 — Айкидо"
    )


def get_bot_response(chat_id, text):
    text = text.strip()
    state = user_states.get(chat_id, "MAIN_MENU")

    if state == "MAIN_MENU":
        if text == "1":
            user_states[chat_id] = "ART_DETAILS"
            return (
                "🎨 Студия Сейталиев Арт предлагает:\n"
                "- Эстетический курс (6-12 лет)\n"
                "- Академический рисунок (база и для поступающих)\n"
                "- Живопись и мастер-классы\n\n"
                "Напишите 'да', чтобы мы перезвонили вам для записи на пробное занятие!"
            )
        elif text == "2":
            user_states[chat_id] = "ORT_DETAILS"
            return (
                "📚 Подготовка к ОРТ (онлайн/оффлайн):\n"
                "У нас есть 13 пакетов обучения (Математика, Родной язык, Физика, Биология, Химия).\n"
                "Напишите 'инфо', чтобы получить список всех пакетов."
            )
        elif text == "3":
            return (
                "🌍 Языковые курсы:\n"
                "Групповые и индивидуальные занятия по английскому, немецкому, русскому и кыргызскому языкам.\n"
                "Оставьте сообщение, и мы перезвоним вам!"
            )
        elif text == "4":
            return (
                "📐 Предметные курсы:\n"
                "Подтянем знания по математике, физике, химии и биологии.\n"
                "Наши педагоги помогут добиться лучших результатов."
            )
        elif text == "5":
            return (
                "🥋 Федерация Айкидо КР:\n"
                "Тренировки для детей и взрослых. Наши залы находятся по всему городу.\n"
                "Напишите нам, и мы подберем ближайший зал!"
            )
        else:
            return get_main_menu()

    user_states[chat_id] = "MAIN_MENU"
    return "Благодарим за интерес! Чтобы вернуться в меню, напишите любой текст."


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
