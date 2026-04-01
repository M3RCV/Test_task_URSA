import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (если он существует)
load_dotenv()

# Получаем значения из окружения
TOKEN = os.getenv("PANDASCORE_TOKEN")
URL = os.getenv("URL", "https://api.pandascore.co")

# Проверяем, что обязательные переменные заданы
if not TOKEN:
    raise ValueError("PANDASCORE_TOKEN не задан в переменных окружения или .env файле")