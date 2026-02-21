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
    "ru": {
        "menu_title": "Пожалуйста, выберите, что вас интересует:",
        "btn_art": "🎨 Сейталиев Арт (Рисование)",
        "btn_ort": "🎓 ОРТ Vector",
        "btn_lang": "🇬🇧 Языковые курсы",
        "btn_school": "📐 Школьные предметы",
        "btn_aikido": "🥋 Айкидо",

        "art": "Вас приветствует Центр Наук и Искусств – студия Сейталиев Арт.\n\n"
               "Наша студия предлагает Вам:\n"
               "• Эстетический курс для детей с 6 до 12 лет для развития вкуса и воображения.\n"
               "• Академический рисунок — база: пропорции, штрих, перспектива, для подростков и взрослых.\n"
               "• Академический рисунок для поступающих — подготовка к экзаменам.\n"
               "• Живопись — работа с цветом и материалами. Композиция.\n"
               "• Рисование на планшете.\n"
               "• Мастер-классы для детей и взрослых — формат одного занятия.\n\n"
               "С нашими профессиональными педагогами вы сможете добиться лучших результатов!",

        "ort": "Вас приветствует Центр Наук и Искусств – проект Vector.\n\n"
               "Наш Центр предлагает Вам видеокурсы ОРТ, онлайн и офлайн курсы ОРТ. Вы можете выбрать:\n"
               "• Пакет 1 (МР-1): математика/русский язык\n"
               "• Пакет 2 (МРБХ-1): математика/русский язык/биология/химия\n"
               "• Пакет 3 (МРФ-1): математика/русский/физика\n"
               "• Пакет 4 (МРА-1): мат/рус/английский\n"
               "• Пакет 5 (М-1): математика на русском\n"
               "• Пакет 6 (Р-1): русский язык\n"
               "• Пакет 7 (БХ-1): биология/химия",

        "lang": "Вас приветствует Центр Наук и Искусств.\n\n"
                "Наш Центр предлагает Вам языковые курсы в группах и индивидуально по:\n"
                "🇬🇧 Английскому языку\n"
                "🇰🇬 Кыргызскому языку\n"
                "🇩🇪 Немецкому языку\n"
                "🇷🇺 Русскому языку",

        "school": "Наш Центр предлагает Вам подтянуть в группах и индивидуально математику, физику, химию и биологию.\n\n"
                  "С нашими преподавателями вы сможете добиться лучших результатов.",

        "aikido": "Вас приветствует Федерация Айкидо Кыргызской Республики.\n\n"
                  "Мы предлагаем тренировки для детей и взрослых. Наши залы находятся:\n"
                  "📍 В здании Цирка\n"
                  "📍 ул. Советская / ул. Боконбаева\n"
                  "📍 Спортзал БГУ\n"
                  "📍 Политех\n"
                  "📍 Школа №60\n"
                  "📍 ул. Ахунбаева / ул. Матросова\n"
                  "📍 7 микрорайон, ДСК",

        "ask_name": "Для получения полной информации и записи, пожалуйста, напишите ваше Имя:",
        "ask_phone": "Отлично! Нажмите кнопку ниже, чтобы быстро поделиться номером телефона, или введите его вручную:",
        "btn_contact": "📱 Отправить мой номер",
        "thanks": "Спасибо! Ваша заявка принята. Наш специалист скоро свяжется с вами для подробной консультации."
    },

    "kg": {
        "menu_title": "Сураныч, сизди кызыктырган багытты тандаңыз:",
        "btn_art": "🎨 Сейталиев Арт (Сүрөт тартуу)",
        "btn_ort": "🎓 ЖРТ (ОРТ) Vector",
        "btn_lang": "🇬🇧 Тил курстары",
        "btn_school": "📐 Мектеп сабактары",
        "btn_aikido": "🥋 Айкидо",

        "art": "Илим жана Искусство борборундагы – “Сейталиев Арт” студиясына кош келдиңиз.\n\n"
               "Биздин студия сизге төмөндөгүлөрдү сунуштайт:\n"
               "• 6 жаштан 12 жашка чейинки балдар үчүн эстетикалык табитти өстүрүүчү курс.\n"
               "• Академиялык сүрөт тартуу — негизги база: пропорция, штрих, перспектива.\n"
               "• Жогорку окуу жайга тапшыруучулар үчүн — экзаменге даярдык.\n"
               "• Живопись — түстөр жана материалдар менен иштөө.\n"
               "• Планшетте сүрөт тартуу.\n"
               "• Балдар жана чоңдор үчүн мастер-класстар.\n\n"
               "Биздин кесипкөй педагогдор менен мыкты жыйынтыктарга жете аласыздар!",

        "ort": "Илим жана Искусство борборундагы – Вектор ЖРТга даярдоо курсуна кош келиңиз.\n\n"
               "Биз сизге ЖРТга даярдоочу видеосабак жана онлайн/офлайн курстарын сунуштайбыз:\n"
               "• 1-пакет (МК-1): математика/кыргыз тили\n"
               "• 2-пакет (МКБХ-1): математика/кыргыз тили/биология/химия\n"
               "• 3-пакет (МКФ-1): математика/кыргыз тили/физика\n"
               "• 4-пакет (МКА-1): математика/кыргыз/англис\n"
               "• 5-пакет (М-1): математика гана\n"
               "• 6-пакет (К-1): кыргыз тили гана\n"
               "• 7-пакет (БХ-1): биология/химия",

        "lang": "Илим жана Искусство борборуна кош келиңиз.\n\n"
                "Биз сизге төмөнкү тил курстарын группа жана жеке форматта сунуштайбыз:\n"
                "🇬🇧 Англис тили\n"
                "🇰🇬 Кыргыз тили\n"
                "🇩🇪 Немец тили\n"
                "🇷🇺 Орус тили",

        "school": "Биздин борбор сизге математика, физика, химия жана биология сабактарын группада жана жеке форматта тереңдетип окууну сунуштайт.\n\n"
                  "Биздин мугалимдер менен сиз эң жакшы жыйынтыктарга жете аласыз.",

        "aikido": "Кыргыз Республикасынын Айкидо федерациясына кош келиңиз.\n\n"
                  "Биз балдар жана чоңдор үчүн машыгууларды сунуштайбыз. Биздин залдар:\n"
                  "📍 Цирктин имаратында\n"
                  "📍 Совет / Бөкөнбаев көчөлөрү\n"
                  "📍 БГУнун спортзалы\n"
                  "📍 Политех\n"
                  "📍 №60 мектеп\n"
                  "📍 Ахунбаев / Матросов көчөлөрү\n"
                  "📍 7-микрорайон, ДСК",

        "ask_name": "Толук маалымат алуу жана жазылуу үчүн Атыңызды жазыңыз:",
        "ask_phone": "Сонун! Телефон номериңизди жөнөтүү үчүн төмөнкү баскычты басыңыз же кол менен жазыңыз:",
        "btn_contact": "📱 Номеримди жөнөтүү",
        "thanks": "Ыраазычылык билдиребиз! Сиздин билдирүүңүз кабыл алынды. Толук маалымат берүү үчүн биздин адис сизге байланышка чыгат."
    }
}


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}

    greeting = (
        "Саламатсызбы! Илим жана Искусство борборуна кош келиңиз.\n"
        "Сураныч, тейлөө тилин тандаңыз.\n\n"
        "Вас приветствует Центр Наук и Искусств.\n"
        "Пожалуйста, выберете язык общения."
    )

    markup = types.InlineKeyboardMarkup()
    btn_kg = types.InlineKeyboardButton("🇰🇬 Кыргыз тили", callback_data="lang_kg")
    btn_ru = types.InlineKeyboardButton("🇷🇺 Русский язык", callback_data="lang_ru")
    markup.add(btn_kg, btn_ru)

    bot.send_message(chat_id, greeting, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def choose_menu(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)

    lang = call.data.split("_")[1]
    user_data[chat_id] = {"lang": lang}

    texts = TEXTS[lang]

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(texts["btn_art"], callback_data="service_art"),
        types.InlineKeyboardButton(texts["btn_ort"], callback_data="service_ort"),
        types.InlineKeyboardButton(texts["btn_lang"], callback_data="service_lang"),
        types.InlineKeyboardButton(texts["btn_school"], callback_data="service_school"),
        types.InlineKeyboardButton(texts["btn_aikido"], callback_data="service_aikido")
    )

    bot.send_message(chat_id, texts["menu_title"], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("service_"))
def service_info(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)

    service_key = call.data.split("_")[1]
    lang = user_data.get(chat_id, {}).get("lang", "ru")  # По умолчанию русский, если сбой
    texts = TEXTS[lang]

    user_data[chat_id]["service"] = service_key

    bot.send_message(chat_id, texts[service_key])

    msg = bot.send_message(chat_id, texts["ask_name"])
    bot.register_next_step_handler(msg, get_name)


def get_name(message):
    chat_id = message.chat.id
    lang = user_data.get(chat_id, {}).get("lang", "ru")
    texts = TEXTS[lang]

    user_data[chat_id]["name"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_btn = types.KeyboardButton(text=texts["btn_contact"], request_contact=True)
    markup.add(contact_btn)

    msg = bot.send_message(chat_id, texts["ask_phone"], reply_markup=markup)
    bot.register_next_step_handler(msg, get_phone)


def get_phone(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "Произошла ошибка сессии. Пожалуйста, нажмите /start")
        return

    lang = user_data[chat_id]["lang"]
    texts = TEXTS[lang]
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
    service_full_name = services_names.get(user_data[chat_id]["service"], "Неизвестно")

    save_data("Telegram", name, phone, service_full_name)

    remove_markup = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, texts["thanks"], reply_markup=remove_markup)

    user_data.pop(chat_id, None)


if __name__ == '__main__':
    print("----- Telegram бот запущен... -----")
    bot.polling(none_stop=True)