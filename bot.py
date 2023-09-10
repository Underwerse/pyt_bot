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

FGA_CENSORED_API_URL='http://fucking-great-advice.ru/api/random/censored'
FGA_UNCENSORED_API_URL='http://fucking-great-advice.ru/api/random'

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)
# Создаем экземпляр переводчика
global translator
translator = Translator()
chat_id = None

# Определяем глобальные переменные для последующего обращения к API
global instructionsRequired
instructionsRequired = True
# Глобальный словарь с переводами кухонь
cuisine_translations = {
    "Африканская": "African",
    "Азиатская": "Asian",
    "Американская": "American",
    "Британская": "British",
    "Карибская": "Caribbean",
    "Китайская": "Chinese",
    "Восточноевропейская": "Eastern European",
    "Европейская": "European",
    "Французская": "French",
    "Немецкая": "German",
    "Греческая": "Greek",
    "Индийская": "Indian",
    "Итальянская": "Italian",
    "Японская": "Japanese",
    "Корейская": "Korean",
    "Средиземноморская": "Mediterranean",
    "Мексиканская": "Mexican",
    "Скандинавская": "Nordic",
    "Испанская": "Spanish",
    "Тайская": "Thai",
    "Вьетнамская": "Vietnamese"
}
diet_translations = {
    "Безглютеновая": "Gluten Free", 
    "Вегетарианская": "Vegetarian", 
    "Веганская": "Vegan", 
    "Обычная": ""
}
# Используем переведенные названия для отображения на кнопках меню
translated_cuisines = list(cuisine_translations.keys())
translated_diets = list(diet_translations.keys())

# markup для скрытия клавиатуры
hide_markup = types.ReplyKeyboardRemove()
# markup для показа начального меню выбора
start_over_button = types.KeyboardButton("Начать поиск рецепта")
get_advice_button = types.KeyboardButton("Дай-ка лучше мне совет")
markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
markup.add(start_over_button, get_advice_button)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # global chat_id
    chat_id = message.chat.id
    
    bot.send_message(chat_id, "Хэлоу, я бот-объебот (в смысле объедение-бот), помогаю в поиске рецептов блюд и еще могу дать совет", reply_markup=markup)

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    # Число кнопок меню в ряд
    row_width = 3
    global selected_cuisine, selected_diet, ingredients, translated_cuisines, translated_diets

    if message.text == "Начать поиск рецепта":
        cuisine_markup = types.ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True)

        # Разбиваем массив на подмассивы по row_width элементов и добавляем их в клавиатуру
        for i in range(0, len(translated_cuisines), row_width):
            row = translated_cuisines[i:i + row_width]
            cuisine_markup.row(*row)

        bot.send_message(chat_id, "Выбери тип кухни:", reply_markup=cuisine_markup)
    elif message.text in translated_cuisines:
        selected_cuisine = cuisine_translations[message.text]
        bot.send_message(chat_id, f"Ты выбрал тип кухни: {message.text}")

        # Создаем клавиатуру для выбора диеты
        diet_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

        # Разбиваем массив на подмассивы по 2 элемента и добавляем их в клавиатуру
        for i in range(0, len(translated_diets), 2):
            row = translated_diets[i:i + 2]
            diet_markup.row(*row)

        bot.send_message(chat_id, "Выбери диету:", reply_markup=diet_markup)
    elif message.text in translated_diets:
        selected_diet = diet_translations[message.text]
        bot.send_message(chat_id, f"Ты выбрал диету: {message.text}\nТеперь перечисли через запятую хотя бы два желаемых ингредиента для рецепта", reply_markup=hide_markup)
    elif ',' in message.text:
        ingredients = translator.translate(message.text, src='ru', dest='en').text.replace(', ', ',')

        bot.send_message(chat_id, f"Ты выбрал ингредиенты: {message.text}")
        # Добавляем кнопку "Найти рецепты"
        find_recipes_button = types.KeyboardButton("Найти рецепты")
        additional_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        additional_markup.add(find_recipes_button)
        bot.send_message(chat_id, "Теперь нажми 'Найти рецепты' для поиска рецептов.", reply_markup=additional_markup)
    elif message.text == "Найти рецепты":
        if selected_cuisine or selected_diet or ingredients:
            search_recipe(message, True)
        else:
            bot.send_message(chat_id, "Пожалуйста, выбери тип кухни, диету и ингредиенты сначала.")
    elif message.text == "Дай-ка лучше мне совет":
        give_advice(message)
    else:
        bot.send_message(chat_id, "Похоже, ты указал 1 ингредиент ну или написал отсебятину. Посмотри еще раз сообщение выше и сделай как сказали, блеать!")

# Функция поиска рецептов. regular сделал для обработки кейса, когда рецепты по ингредиентам не найдены и мы ищем без их учета (URL меняем)
def search_recipe(message, regular):
    response = None
    if regular:
        response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={FOOD_API_KEY}&cuisine={selected_cuisine}&diet={selected_diet}&includeIngredients={ingredients}")
    else:
        response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={FOOD_API_KEY}&cuisine={selected_cuisine}&diet={selected_diet}")

    if response.status_code == 200:
        data = response.json()
        recipes = data.get("results")

        if recipes:
            bot.reply_to(message, "Нашел для тебя кое-что:", reply_markup=markup)
            for i, recipe in enumerate(recipes[:3]):
                recipe_id = recipe.get("id")
                # Получаем подробности рецепта по его id
                recipe_info_response = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?includeNutrition=false&apiKey={FOOD_API_KEY}")
                if recipe_info_response.status_code == 200:
                    recipe_info = recipe_info_response.json()
                    title = recipe_info.get("title")
                    link = recipe_info.get("sourceUrl")
                    image = recipe_info.get("image")

                    # Отправляем рецепт в сообщении
                    bot.send_message(message.chat.id, f"{i + 1}. {translator.translate(title, src='en', dest='ru').text}: {link}")
                    bot.send_photo(message.chat.id, image, caption=f"![{title}]({image})")
            # else:
            #     bot.reply_to(message, "Сорян, но об одном из рецептов не удалось получить информацию.")
        else:
            # Проверяем, был ли запрос regular или даже без regular ничего не найдено
            if regular:
                bot.reply_to(message, "Сорян, но я что-то не смог найти рецептов по такому запросу, поэтому давай-ка поищем что-то без учета ингредиентов...")
                search_recipe(message, False)
            else:
                bot.reply_to(message, "Сорян, но я что-то не смог найти рецептов по такому запросу.")
            
            
            bot.send_message(message.chat.id, "Погнали искать тебе рецепт! Ну или совет может хочешь?", reply_markup=markup)
    else:
        bot.reply_to(message, "Сорян, но произошла ошибка из-за кривых рук программёра.")

# Функция поиска совета
def give_advice(message):
    chat_id = message.chat.id
    # Отправляем запрос к API для поиска рецептов (БЕЗ цензуры)
    response = requests.get(FGA_UNCENSORED_API_URL)
    advice = None

    if response.status_code == 200:
        data = response.json()
        advice = data.get("text")

    if advice:
        bot.send_message(chat_id, advice, reply_markup=markup)
    else:
        bot.reply_to(message, "Сорян, но что-то нет у меня для тебя советов.", reply_markup=markup)

# Запуск бота
if __name__ == "__main__":
    bot.polling()