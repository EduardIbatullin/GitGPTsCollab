# app/config.py

import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Получаем необходимые переменные окружения
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')

# Если токен не найден, выводим ошибку
if GITHUB_TOKEN is None:
    raise ValueError("Не удалось найти TELEGRAM_BOT_TOKEN в .env файле")

# Если имя пользователя не найдено, выводим ошибку
if GITHUB_USERNAME is None:
    raise ValueError("Не удалось найти GITHUB_USERNAME в .env файле")
