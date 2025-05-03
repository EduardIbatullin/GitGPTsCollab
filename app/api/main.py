# app/api/main.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import repo_router
from app.core.exceptions import GitHubAPIError

app = FastAPI(title="GitHub Repo Assistant API")

@app.exception_handler(GitHubAPIError)
async def handle_github_api_error(request: Request, exc: GitHubAPIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)}
    )

# Подключаем роутеры
app.include_router(repo_router.router)
