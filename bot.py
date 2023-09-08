import telebot
from telebot import types
# Библиотеки для работы с переменными окружения (.env)
from dotenv import load_dotenv
import os
# Библиотеки для API-запросов
import requests

# Загружаем переменные окружения из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
FOOD_API_KEY=os.getenv("FOOD_API_KEY")

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    global chat_id
    chat_id = message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    item1 = telebot.types.KeyboardButton("Выбери тип кухни")
    markup.add(item1)
    bot.send_message(chat_id, "Хэлоу, я бот-объебот (в смысле объедение-бот), помогаю в поиске рецептов блюд", reply_markup=markup)

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global selected_cuisine
    global selected_diet
    global cuisines
    global diets
    global ingredients
    row_width=3
    if message.text == "Выбери тип кухни":
        cuisine_markup = telebot.types.ReplyKeyboardMarkup(row_width=row_width)
        cuisines = ["African", "Asian", "American", "British", "Cajun", "Caribbean", "Chinese", "Eastern European",
                    "European", "French", "German", "Greek", "Indian", "Irish", "Italian", "Japanese", "Jewish",
                    "Korean", "Latin American", "Mediterranean", "Mexican", "Middle Eastern", "Nordic", "Southern",
                    "Spanish", "Thai", "Vietnamese"]
        # Разбиваем массив на подмассивы по row_width элементов и добавляем их в клавиатуру
        for i in range(0, len(cuisines), row_width):
            row = cuisines[i:i+row_width]
            cuisine_markup.row(*row)
        
        bot.send_message(chat_id, "Выбери тип кухни:", reply_markup=cuisine_markup)
    elif message.text in cuisines:
        selected_cuisine = message.text
        bot.send_message(chat_id, f"Ты выбрал тип кухни: {selected_cuisine}")
        
        # Создаем клавиатуру для выбора диеты
        diet_markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        diets = ["Gluten Free", "Vegetarian", "Vegan", "Regular"]
        
        # Разбиваем массив на подмассивы по row_width элементов и добавляем их в клавиатуру
        for i in range(0, len(diets), 2):
            row = diets[i:i+2]
            diet_markup.row(*row)
        
        bot.send_message(chat_id, "Выбери диету:", reply_markup=diet_markup)
    elif message.text in diets:
        selected_diet = message.text
        bot.send_message(chat_id, f"Ты выбрал диету: {selected_diet}\nТеперь перечисли через запятую, какие ты хочешь использовать ингредиенты")
                
        
    elif ', ' in message.text:
        ingredients = [ingredient.strip() for ingredient in message.text.split(',')]
        bot.send_message(chat_id, f"Ты выбрал ингредиенты: {', '.join(ingredients)}")
    else:
        bot.send_message(chat_id, "Пожалуйста, используйте кнопки для выбора опции.")

# Запуск бота
if __name__ == "__main__":
    bot.polling()