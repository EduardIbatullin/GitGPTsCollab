# app/domain/services/github_service.py

import base64

from app.infrastructure.github_client import GitHubClient
from app.domain.models import RepoStructureResponse, FileContentResponse


class GitHubService:
    """
    Сервис для работы с GitHub API.

    Используется для получения структуры репозитория, содержимого файлов
    и создания новых файлов на GitHub.
    """
    def __init__(self, github_client: GitHubClient):
        """
        Инициализация сервиса GitHub.

        Args:
            github_client (GitHubClient): Экземпляр клиента для работы с GitHub API.
        """
        self.github_client = github_client

    async def get_repo_structure(self, repo: str) -> list:
        """
        Получение структуры репозитория на GitHub.

        Args:
            repo (str): Имя репозитория.

        Returns:
            list: Структура репозитория.
        """
        return await self.github_client.list_repo_tree(repo)

    async def get_file_content(self, repo: str, path: str) -> FileContentResponse:
        """
        Получение и декодирование содержимого файла из репозитория.

        1. Вызывает инфраструктурный клиент, чтобы получить JSON с Base64.
        2. Декодирует поле 'content' из Base64 в UTF-8.
        3. Оборачивает результат в Pydantic-модель FileContentResponse.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к файлу.

        Returns:
            FileContentResponse: Содержимое файла в виде строки и кодировка.
        """
        api_data = await self.github_client.get_file_content(repo, path)
        raw_b64 = api_data.get("content", "")
        decoded_text = base64.b64decode(raw_b64).decode("utf-8")
        return FileContentResponse(
            path=path,
            content=decoded_text,
            encoding="utf-8"
        )

    async def create_file(self, repo: str, path: str, filename: str, content: str, message: str) -> FileContentResponse:
        """
        Создание нового файла в репозитории на GitHub.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к папке.
            filename (str): Имя файла.
            content (str): Содержимое файла.
            message (str): Сообщение коммита.

        Returns:
            FileContentResponse: Ответ с созданным файлом.
        """
        result = await self.github_client.create_file(repo, path, filename, content, message)
        # Извлекаем информацию о файле из ответа API
        file_info = result['content']
        # Возвращаем реальный путь к файлу и исходное содержимое
        return FileContentResponse(
            path=file_info['path'],
            content=content,
            encoding='utf-8'
        )
