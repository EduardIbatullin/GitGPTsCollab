# app/core/config.py

import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Получаем необходимые переменные окружения
MY_GITHUB_TOKEN = os.getenv('MY_GITHUB_TOKEN')
MY_GITHUB_USERNAME = os.getenv('MY_GITHUB_USERNAME')

if MY_GITHUB_TOKEN is None:
    raise ValueError("Не удалось найти MY_GITHUB_TOKEN в переменных окружения")

if MY_GITHUB_USERNAME is None:
    raise ValueError("Не удалось найти MY_GITHUB_USERNAME в переменных окружения")
