# app/infrastructure/github_client.py

import base64
import httpx

from app.core.config import MY_GITHUB_TOKEN, MY_GITHUB_USERNAME

class GitHubClient:
    """
    Клиент для работы с GitHub API.
    
    Предоставляет методы для получения структуры репозитория, содержимого файлов
    и создания новых файлов в репозитории.
    """
    def __init__(self):
        """
        Инициализация GitHub клиента с базовым URL и заголовками.
        """
        self.base_url = "https://api.github.com"
        self.headers = {"Authorization": f"Bearer {MY_GITHUB_TOKEN}"}

    async def list_repo_tree(self, repo: str) -> list:
        """
        Получение структуры репозитория.

        Args:
            repo (str): Имя репозитория.

        Returns:
            list: Список файлов и папок в репозитории.
        """
        url = f"{self.base_url}/repos/{MY_GITHUB_USERNAME}/{repo}/contents"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
        return response.json()

    async def get_file_content(self, repo: str, path: str) -> dict:
        """
        Получение содержимого файла из репозитория.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к файлу.

        Returns:
            dict: Содержимое файла и его кодировка.
        """
        url = f"{self.base_url}/repos/{MY_GITHUB_USERNAME}/{repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
        return response.json()

    async def create_file(
        self, repo: str, path: str, filename: str, content: str, message: str
    ) -> dict:
        """
        Создание нового файла в репозитории.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к папке (без ведущего '/').
            filename (str): Имя файла.
            content (str): Текстовое содержимое файла.
            message (str): Сообщение коммита.

        Returns:
            dict: JSON-ответ GitHub API.
        """
        # 1) кодируем текст в Base64
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("ascii")

        # 2) собираем URL к файлу
        if path:
            url_path = f"{path.rstrip('/')}/{filename}"
        else:
            url_path = filename

        url = f"{self.base_url}/repos/{MY_GITHUB_USERNAME}/{repo}/contents/{url_path}"
        data = {
            "message": message,
            "content": encoded_content,
        }

        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=data, headers=self.headers)

        # если статус не 201 Created — пробрасываем ошибку
        response.raise_for_status()
        return response.json()
