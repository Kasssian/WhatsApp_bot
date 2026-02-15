import os

import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

from database import save_data

load_dotenv()
app = Flask(__name__)

WA_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

user_state = {}

TEXT_ART = (
    "Вас приветствует Центр Наук и Искусств – студия Сейталиев Арт. Благодарим, что позвонили нам.\n\n"
    "Наша студия предлагает Вам:\n"
    "• Эстетический курс для детей с 6 до 12 лет для развития вкуса и воображения.\n"
    "• Академический рисунок — база: пропорции, штрих, перспектива, для подростков и взрослых.\n"
    "• Академический рисунок для поступающих — подготовка к экзаменам.\n"
    "• Живопись — работа с цветом и материалами. Композиция.\n"
    "• Мастер-классы для детей и взрослых — формат одного занятия.\n"
    "• Рисование на планшете.\n\n"
    "С нашими профессиональными педагогами вы сможете добиться лучших результатов. "
    "Ваши твердые навыки станут надежным фундаментом для будущей профессии ваших детей, и источников вдохновения для взрослых."
)

TEXT_ORT = (
    "Вас приветствует Центр Наук и Искусств – проект Vector. Благодарим, что позвонили нам.\n\n"
    "Наш Центр предлагает Вам на выбор целыми пакетами, либо по отдельным предметами понятные видеокурсы, офлайн или онлайн уроки по ОРТ в группах и индивидуально:\n\n"
    "Пакет 1 (ПР-1): мат/рус\n"
    "Пакет 2 (ПК-1): мат/кырг\n"
    "Пакет 3 (ПРФ-1): мат/рус/физ\n"
    "Пакет 4 (ПРА-1): мат/рус/англ\n"
    "Пакет 5 (ПРБХ-1): мат/рус/био/хим\n"
    "Пакет 6 (ПКФ-1): мат/кырг/физ\n"
    "Пакет 7 (ПКБХ-1): мат/кырг/био/хим\n"
    "Пакет 8 (ПМР-1): мат на русском\n"
    "Пакет 9 (ПМК-1): мат на кыргызском\n"
    "Пакет 10 (ПР-1): русский язык\n"
    "Пакет 11 (ПК-1): кыргызский язык\n"
    "Пакет 12 (ПМРИ-1): биология/химия.\n\n"
    "С нашими педагогами вы сможете добиться лучших результатов."
)

TEXT_LANG = (
    "Вас приветствует Центр Наук и Искусств. Благодарим, что позвонили нам.\n\n"
    "Наш Центр предлагает Вам языковые курсы в группах и индивидуально по:\n"
    "• Английскому языку;\n"
    "• Кыргызскому языку;\n"
    "• Немецкому языку;\n"
    "• Русскому языку.\n\n"
    "С нашими педагогами вы сможете добиться лучших результатов."
)

TEXT_SCHOOL = (
    "Наш Центр предлагает Вам подтянуть в группах и индивидуально математику, физику, химию и биологию.\n\n"
    "С нашими педагогами вы сможете добиться лучших результатов."
)

TEXT_AIKIDO = (
    "Вас приветствует Федерация Айкидо Кыргызской Республики. Благодарим Вас за звонок.\n\n"
    "Мы предлагаем тренировки для детей и взрослых. Наши залы находятся по адресам: [Адреса]\n\n"
    "Будем рады видеть Вас на наших тренировках."
)


def send_message(to_number, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)


def process_message(wa_id, text):
    text = text.strip()

    if wa_id not in user_state:
        user_state[wa_id] = {"step": "CHOOSE_LANG"}
        greeting = (
            "Вас приветствует Центр Наук и Искусств. Благодарим, что написали нам.\n\n"
            "Выберите пожалуйста язык общения:\n"
            "Отправьте 1️⃣ для кыргызского языка.\n"
            "Отправьте 2️⃣ для русского языка."
        )
        send_message(wa_id, greeting)
        return

    step = user_state[wa_id]["step"]

    if step == "CHOOSE_LANG":
        if text == "2":
            user_state[wa_id]["step"] = "CHOOSE_SERVICE"
            menu = (
                "Что вас интересует? Отправьте цифру нужного пункта:\n\n"
                "1️⃣ Курсы рисования, живописи, мастер классы\n"
                "2️⃣ Курсы подготовки к ОРТ\n"
                "3️⃣ Языковые курсы (английский, русский, кыргызский, немецкий)\n"
                "4️⃣ Школьные предметы (математика, физика, биология и химия)\n"
                "5️⃣ Информация по Айкидо"
            )
            send_message(wa_id, menu)
        elif text == "1":
            send_message(wa_id,
                         "Кечиресиз, кыргыз тилиндеги меню даярдалууда. Пожалуйста, отправьте цифру 2 для выбора русского языка.")
        else:
            send_message(wa_id, "Пожалуйста, отправьте цифру 1 или 2.")

    elif step == "CHOOSE_SERVICE":
        service_map = {
            "1": ("Сейталиев Арт", TEXT_ART),
            "2": ("ОРТ Vector", TEXT_ORT),
            "3": ("Языки", TEXT_LANG),
            "4": ("Школьные предметы", TEXT_SCHOOL),
            "5": ("Айкидо", TEXT_AIKIDO)
        }

        if text in service_map:
            service_name, service_text = service_map[text]
            user_state[wa_id]["step"] = "ENTER_NAME"
            user_state[wa_id]["service"] = service_name

            send_message(wa_id, service_text + "\n\nДля получения полной информации, напишите ваше Имя:")
        else:
            send_message(wa_id, "Пожалуйста, отправьте цифру от 1 до 5.")

    elif step == "ENTER_NAME":
        name = text
        phone = wa_id
        service = user_state[wa_id]["service"]

        save_data("WhatsApp", name, phone, service)

        send_message(wa_id,
                     f"Спасибо, {name}! Ваша заявка принята. Наш администратор скоро свяжется с вами по номеру +{phone}.")

        del user_state[wa_id]


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    if request.method == 'POST':
        data = request.json
        try:
            message_info = data['entry'][0]['changes'][0]['value']['messages'][0]
            wa_id = message_info['from']
            text = message_info['text']['body']

            process_message(wa_id, text)
        except KeyError:
            pass

        return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
