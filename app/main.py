"""
main.py

FastAPI-приложение для работы с репозиториями GitHub:
- Получение структуры репозитория
- Получение содержимого файла
- Создание нового файла
"""

import logging
from fastapi import FastAPI, Path, Query, status, Request, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import httpx

from app.github_client import list_repo_tree, get_file_content, create_file

# Настраиваем собственный логгер
logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logger.addHandler(handler)

app = FastAPI(title="GitHub Repo Assistant API")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"← {request.method} {request.url.path} — {response.status_code}")
    return response


class RepoStructureResponse(BaseModel):
    """Модель ответа для эндпоинта структуры репозитория."""
    repo: str
    tree: list


class FileContentResponse(BaseModel):
    """Модель ответа для эндпоинта получения содержимого файла."""
    path: str
    content: str
    encoding: str


class CreateFileRequest(BaseModel):
    """Модель запроса для создания нового файла в репозитории."""
    path: str = Field(
        ...,
        description="Папка внутри репозитория без ведущего слеша",
        min_length=1
    )
    filename: str = Field(
        ...,
        description="Имя файла (не должно содержать '/')",
        min_length=1,
        pattern=r"^[^/]+$"
    )
    content: str = Field(
        ...,
        description="Текст файла в кодировке UTF-8"
    )
    message: str = Field(
        "Create file via API",
        description="Сообщение коммита"
    )

    @field_validator("path", mode="before")
    @classmethod
    def strip_leading_slash(cls, v: str) -> str:
        """Убирает случайный ведущий слеш из пути."""
        if v.startswith("/"):
            raise ValueError("Путь не должен начинаться с '/'")
        return v


@app.exception_handler(httpx.HTTPStatusError)
async def github_api_error_handler(request: Request, exc: httpx.HTTPStatusError):
    """
    Обработчик ошибок, возвращаемых GitHub API.
    Возвращает JSON с оригинальным кодом и сообщением ошибки.
    """
    status_code = exc.response.status_code
    detail = exc.response.json().get("message", exc.response.text)
    return JSONResponse(
        status_code=status_code if 400 <= status_code < 600 else status.HTTP_502_BAD_GATEWAY,
        content={"detail": f"Ошибка GitHub API: {detail}"}
    )


@app.exception_handler(httpx.RequestError)
async def network_error_handler(request: Request, exc: httpx.RequestError):
    """
    Обработчик сетевых ошибок при запросах к GitHub API
    (тайм-ауты, проблемы DNS и т.п.).
    """
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": f"Сетевая ошибка: {exc}"}
    )


@app.get(
    "/repos/{repo}/structure",
    response_model=RepoStructureResponse,
    summary="Получить структуру репозитория"
)
async def repo_structure(
    repo: str = Path(..., description="Имя репозитория", min_length=1)
):
    """
    Возвращает дерево файлов и папок указанного репозитория.
    """
    tree = await list_repo_tree(repo)
    return {"repo": repo, "tree": tree}


@app.get(
    "/repos/{repo}/file",
    response_model=FileContentResponse,
    summary="Получить содержимое файла"
)
async def file_content(
    repo: str = Path(..., description="Имя репозитория", min_length=1),
    path: str = Query(..., description="Путь к файлу внутри репозитория", min_length=1)
):
    """
    Возвращает содержимое файла по указанному пути.
    """
    return await get_file_content(repo, path)


@app.post(
    "/repos/{repo}/file",
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый файл"
)
async def create_new_file(
    repo: str = Path(..., description="Имя репозитория", min_length=1),
    req: CreateFileRequest = Body(..., description="Параметры нового файла")
):
    """
    Создаёт новый файл по указанному пути с заданным содержимым
    и сообщением коммита.
    """
    full_path = f"{req.path.rstrip('/')}/{req.filename}"
    return await create_file(repo, full_path, req.content, req.message)
