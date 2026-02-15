import os

import telebot
from dotenv import load_dotenv
from telebot import types

from database import save_data

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_data = {}

TEXTS = {
    "greeting": "Вас приветствует Центр Наук и Искусств. Благодарим, что позвонили нам.\n\nВыберете пожалуйста язык общения. / Тилди тандаңыз.",

    "menu_ru": "Что вас интересует?\n\n"
               "🎨 1. Курсы рисования, живописи, мастер классы для детей и взрослых\n"
               "🎓 2. Курсы подготовки к ОРТ\n"
               "🇬🇧 3. Языковые курсы (английский, русский, кыргызский, немецкий)\n"
               "📐 4. Школьные предметы (математика, физика, биология, химия)\n"
               "🥋 5. Информация по Айкидо",

    "art": "Вас приветствует Центр Наук и Искусств – студия Сейталиев Арт. Благодарим, что позвонили нам.\n\n"
           "Наша студия предлагает Вам:\n"
           "• Эстетический курс для детей с 6 до 12 лет для развития вкуса и воображения.\n"
           "• Академический рисунок — база: пропорции, штрих, перспектива, для подростков и взрослых.\n"
           "• Академический рисунок для поступающих — подготовка к экзаменам.\n"
           "• Живопись — работа с цветом и материалами. Композиция.\n"
           "• Мастер-классы для детей и взрослых — формат одного занятия.\n"
           "• Рисование на планшете.\n\n"
           "С нашими профессиональными педагогами вы сможете добиться лучших результатов по всем направлениям нашей студии. Ваши твердые навыки станут надежным фундаментом для будущей профессии ваших детей, и источников вдохновения для взрослых.",

    "ort": "Вас приветствует Центр Наук и Искусств – проект Vector. Благодарим, что позвонили нам.\n\n"
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
           "С нашими педагогами вы сможете добиться лучших результатов.",

    "lang": "Вас приветствует Центр Наук и Искусств. Благодарим, что написали нам.\n\n"
            "Наш Центр предлагает Вам языковые курсы в группах и индивидуально по:\n"
            "• Английскому языку;\n"
            "• Кыргызскому языку;\n"
            "• Немецкому языку;\n"
            "• Русскому языку.\n\n"
            "С нашими педагогами вы сможете добиться лучших результатов.",

    "school": "Наш Центр предлагает Вам подтянуть в группах и индивидуально математику, физику, химию и биологию.\n\n"
              "С нашими педагогами вы сможете добиться лучших результатов.",

    "aikido": "Вас приветствует Федерация Айкидо Кыргызской Республики. Благодарим Вас за обращение.\n\n"
              "Мы предлагаем тренировки для детей и взрослых. Наши залы находятся по адресам: [Здесь нужно вписать адреса].\n\n"
              "Будем рады видеть Вас на наших тренировках."
}


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Кыргыз тили", callback_data="lang_kg")
    btn2 = types.InlineKeyboardButton("Русский язык", callback_data="lang_ru")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, TEXTS["greeting"], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def choose_menu(call):
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎨 Рисование и живопись", callback_data="service_art"),
        types.InlineKeyboardButton("🎓 Подготовка к ОРТ", callback_data="service_ort"),
        types.InlineKeyboardButton("🇬🇧 Языковые курсы", callback_data="service_lang"),
        types.InlineKeyboardButton("📐 Школьные предметы", callback_data="service_school"),
        types.InlineKeyboardButton("🥋 Айкидо", callback_data="service_aikido")
    )
    bot.send_message(call.message.chat.id, TEXTS["menu_ru"], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("service_"))
def service_info(call):
    bot.answer_callback_query(call.id)
    service_key = call.data.split("_")[1]
    bot.send_message(call.message.chat.id, TEXTS[service_key])

    user_data[call.message.chat.id] = {"service": service_key}
    msg = bot.send_message(call.message.chat.id,
                           "Для записи или получения полной информации, напишите ваше Имя, и мы свяжемся с вами:")
    bot.register_next_step_handler(msg, get_name)


def get_name(message):
    user_data[message.chat.id]["name"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_btn = types.KeyboardButton(text="📱 Отправить мой номер", request_contact=True)
    markup.add(contact_btn)

    msg = bot.send_message(
        message.chat.id,
        "Отлично! Нажмите кнопку ниже, чтобы быстро поделиться номером телефона, или введите его вручную:",
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, get_phone)


def get_phone(message):
    chat_id = message.chat.id
    name = user_data[chat_id]["name"]

    if message.contact is not None:
        phone = message.contact.phone_number
    else:
        phone = message.text

    services_names = {
        "art": "Сейталиев Арт",
        "ort": "ОРТ Vector",
        "lang": "Языки",
        "school": "Школьные предметы",
        "aikido": "Айкидо"
    }
    service_full_name = services_names.get(user_data[chat_id].get("service", ""), "Неизвестно")

    save_data("Telegram", name, phone, service_full_name)

    remove_markup = types.ReplyKeyboardRemove()
    bot.send_message(
        chat_id,
        "Спасибо! Ваша заявка принята. Наш администратор скоро свяжется с вами.",
        reply_markup=remove_markup
    )
    user_data.pop(chat_id, None)


if __name__ == '__main__':
    bot.polling(none_stop=True)
