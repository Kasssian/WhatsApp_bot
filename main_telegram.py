import os

import telebot
from dotenv import load_dotenv

from ai_handler import get_ai_response
from database import save_data

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    bot.send_chat_action(chat_id, 'typing')

    ai_reply = get_ai_response(chat_id, text)

    if "||ЗАЯВКА:" in ai_reply:
        try:
            # Вытаскиваем данные клиента
            secret_line = ai_reply.split("||ЗАЯВКА:")[1].split("||")[0].strip()
            data_parts = secret_line.split(",")

            name = data_parts[0].strip()
            phone = data_parts[1].strip()
            service = data_parts[2].strip()

            save_data("Telegram", name, phone, service)

            ai_reply = ai_reply.split("||ЗАЯВКА:")[0].strip()
        except Exception as e:
            print(f"Ошибка парсинга заявки: {e}")

    bot.send_message(chat_id, ai_reply)


if __name__ == '__main__':
    print("----- AI Telegram бот запущен... -----")
    bot.polling(none_stop=True)