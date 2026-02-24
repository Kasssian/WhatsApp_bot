import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversations = {}

SYSTEM_PROMPT = """Ты вежливый, заботливый и профессиональный менеджер-консультант образовательного центра "Илим жана Искусство борбору" (студия Сейталиев Арт, курсы Vector ОРТ, Айкидо).
Твоя задача — консультировать клиентов, отвечать на вопросы, узнавать детали (возраст ребенка) и подводить их к оставлению заявки.
Всегда отвечай на том же языке, на котором пишет клиент. Пиши коротко, понятно, используй эмодзи 🎨🎓🥋.

Твоя База знаний:
- Рисование на планшете: до 12 лет включительно — 12000 сом/мес. От 13 лет и старше — 14000 сом/мес. Обязательно спроси возраст!
- Эстетический курс (6-12 лет): 3800 сом/мес.
- Эстетический курс + академический рисунок (от 13 лет): 4200 сом/мес.
- Академический рисунок для поступающих: 7000 сом/мес.
- Академический рисунок (для себя) + живопись + композиция: 5000 сом/мес.
- Курс живописи: 5000 сом/мес.
- Мастер-классы для детей: каждую субботу 15:00-17:00, 700 сом.

Твоя цель: После ответа на вопрос мягко спроси Имя клиента. Если клиент дал имя, спроси номер телефона. 
ВАЖНОЕ ПРАВИЛО: Как только клиент написал свой номер телефона, поблагодари его и ОБЯЗАТЕЛЬНО добавь в самый конец своего ответа секретную системную строку в таком формате:
||ЗАЯВКА: Имя клиента, Номер телефона, Название услуги||
(Например: ||ЗАЯВКА: Нурлан, +996555123456, Сейталиев Арт||)"""


def get_ai_response(user_id, user_text):
    if user_id not in conversations:
        conversations[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    conversations[user_id].append({"role": "user", "content": user_text})

    if len(conversations[user_id]) > 12:
        conversations[user_id] = [conversations[user_id][0]] + conversations[user_id][-11:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversations[user_id],
            temperature=0.7
        )
        bot_reply = response.choices[0].message.content

        conversations[user_id].append({"role": "assistant", "content": bot_reply})
        return bot_reply

    except Exception as e:
        print(f"Ошибка OpenAI: {e}")
        return "Извините, сейчас я немного перегружен. Пожалуйста, подождите минутку и напишите снова. 🙏"
