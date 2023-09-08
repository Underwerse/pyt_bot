import telebot
from telebot import types
# Библиотеки для работы с переменными окружения (.env)
from dotenv import load_dotenv
import os
# Библиотеки для API-запросов
import requests
# Библиотека для перевода введенного юзером текста на англ.
from googletrans import Translator

# Загружаем переменные окружения из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
FOOD_API_KEY=os.getenv("FOOD_API_KEY")

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)
# Создаем экземпляр переводчика
global translator
translator = Translator()

# Определяем глобальные переменные для последующего обращения к API
global instructionsRequired
instructionsRequired = True
# Глобальный словарь с переводами кухонь
cuisine_translations = {
    "Африканская": "African",
    "Азиатская": "Asian",
    "Американская": "American",
    "Британская": "British",
    "Кажунская": "Cajun",
    "Карибская": "Caribbean",
    "Китайская": "Chinese",
    "Восточноевропейская": "Eastern European",
    "Европейская": "European",
    "Французская": "French",
    "Немецкая": "German",
    "Греческая": "Greek",
    "Индийская": "Indian",
    "Ирландская": "Irish",
    "Итальянская": "Italian",
    "Японская": "Japanese",
    "Еврейская": "Jewish",
    "Корейская": "Korean",
    "Латиноамериканская": "Latin American",
    "Средиземноморская": "Mediterranean",
    "Мексиканская": "Mexican",
    "Ближневосточная": "Middle Eastern",
    "Скандинавская": "Nordic",
    "Южная": "Southern",
    "Испанская": "Spanish",
    "Тайская": "Thai",
    "Вьетнамская": "Vietnamese"
}
diet_translations = {
    "Безглютеновая": "Gluten Free", 
    "Вегетарианская": "Vegetarian", 
    "Веганская": "Vegan", 
    "Обычная": "Regular"
}
hide_markup = types.ReplyKeyboardRemove()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    global chat_id
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=1)
    item1 = types.KeyboardButton("Выбери тип кухни")
    markup.add(item1)
    bot.send_message(chat_id, "Хэлоу, я бот-объебот (в смысле объедение-бот), помогаю в поиске рецептов блюд", reply_markup=markup)

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Число кнопок меню в ряд
    row_width=3
    global selected_cuisine, selected_diet, ingredients, translated_cuisines, translated_diets

    if message.text == "Выбери тип кухни":
        cuisine_markup = types.ReplyKeyboardMarkup(row_width=row_width)
        # Используем переведенные названия для отображения на кнопках меню
        translated_cuisines = list(cuisine_translations.keys())
        
        # Разбиваем массив на подмассивы по row_width элементов и добавляем их в клавиатуру
        for i in range(0, len(translated_cuisines), row_width):
            row = translated_cuisines[i:i+row_width]
            cuisine_markup.row(*row)
        
        bot.send_message(chat_id, "Выбери тип кухни:", reply_markup=cuisine_markup)
    elif message.text in translated_cuisines:
        selected_cuisine = message.text
        bot.send_message(chat_id, f"Ты выбрал тип кухни: {selected_cuisine}")
        
        # Создаем клавиатуру для выбора диеты
        diet_markup = types.ReplyKeyboardMarkup(row_width=2)
        translated_diets = list(diet_translations.keys())
        
        # Разбиваем массив на подмассивы по 2 элемента и добавляем их в клавиатуру
        for i in range(0, len(translated_diets), 2):
            row = translated_diets[i:i+2]
            diet_markup.row(*row)
        
        bot.send_message(chat_id, "Выбери диету:", reply_markup=diet_markup)
    elif message.text in translated_diets:
        selected_diet = message.text
        bot.send_message(chat_id, f"Ты выбрал диету: {selected_diet}\nТеперь перечисли через запятую, какие ты хочешь использовать ингредиенты", reply_markup=hide_markup)
                
        
    elif ', ' in message.text:
        # ingredients = [ingredient.strip() for ingredient in message.text.split(',')]

        # Переводим ингредиенты с русского на английский
        # ingredients = [translator.translate(ingredient, src='ru', dest='en').text for ingredient in ingredients]
        ingredients = translator.translate(message.text, src='ru', dest='en').text

        bot.send_message(chat_id, f"Ты выбрал ингредиенты: {message.text}")
    else:
        bot.send_message(chat_id, "Пожалуйста, используй кнопки для выбора опции.")

# Запуск бота
if __name__ == "__main__":
    bot.polling()