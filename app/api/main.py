# app/api/main.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from app.api.routers import repo_router

app = FastAPI(title="GitHub Repo Assistant API")

# Подключаем роутеры
app.include_router(repo_router.router)
