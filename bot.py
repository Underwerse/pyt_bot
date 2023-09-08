import telebot
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
    bot.reply_to(message, "Хэлоу, я бот-объебот (в смысле объедение-бот)")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def search_recipe(message):
    # Получаем текст запроса пользователя
    query = message.text
    
    # Отправляем запрос к API для поиска рецептов
    response = requests.get(f"https://api.spoonacular.com/recipes/complexSearch?apiKey={FOOD_API_KEY}&query={query}&number=5")
    
    if response.status_code == 200:
        data = response.json()
        recipes = data.get("results")
        
        if recipes:
            bot.reply_to(message, "Вот несколько рецептов, которые могут вас заинтересовать:")
            for recipe in recipes:
                title = recipe.get("title")
                link = recipe.get("sourceUrl")
                bot.send_message(message.chat.id, f"{title}: {link}")
        else:
            bot.reply_to(message, "Извините, я не смог найти рецептов по вашему запросу.")
    else:
        bot.reply_to(message, "Извините, произошла ошибка при поиске рецептов.")

# Запуск бота
if __name__ == "__main__":
    bot.polling()