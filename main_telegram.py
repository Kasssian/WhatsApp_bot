import os

import telebot
from dotenv import load_dotenv
from telebot import types

from database import save_data

load_dotenv()

TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TG_TOKEN)

users = {}


@bot.message_handler(commands=['start'])
def start(message):
    msg = bot.send_message(message.chat.id, "Здравствуйте! Как к вам обращаться? (ФИО)")
    bot.register_next_step_handler(msg, get_name)


def get_name(message):
    users[message.chat.id] = {"name": message.text}
    msg = bot.send_message(message.chat.id, "Приятно познакомиться! Напишите ваш номер телефона.")
    bot.register_next_step_handler(msg, get_phone)


def get_phone(message):
    users[message.chat.id]["phone"] = message.text

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Рисование', 'ОРТ', 'Языки', 'Предметы', 'Айкидо')

    msg = bot.send_message(message.chat.id, "Выберите услугу:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_service)


def get_service(message):
    service = message.text
    user_data = users.get(message.chat.id)

    if user_data:
        bot.send_message(message.chat.id, "Спасибо! Заявка принята.", reply_markup=types.ReplyKeyboardRemove())

        save_data("Telegram", user_data['name'], user_data['phone'], service)
    else:
        bot.send_message(message.chat.id, "Ошибка. Нажмите /start")


if __name__ == "__main__":
    print("----- Telegram бот запущен... -----")
    bot.polling(none_stop=True)
