# app/infrastructure/github_client.py

import base64
import httpx
from app.core.config import MY_GITHUB_TOKEN, MY_GITHUB_USERNAME

class GitHubClient:
    """
    Клиент для работы с GitHub API.

    Предоставляет методы для CRUD-файлов и получения структуры репозитория.
    """
    def __init__(self):
        """
        Инициализация GitHub клиента с базовым URL и заголовками.
        """
        self.base_url = "https://api.github.com"
        self.headers = {"Authorization": f"Bearer {MY_GITHUB_TOKEN}"}

    # async def get_repo_info(self, repo: str) -> dict:
    #     """
    #     Получить информацию о репозитории.
    #     Позволяет отличить 404 по репозиторию от 404 по файлу.
    #     """
    #     url = f"{self.base_url}/repos/{MY_GITHUB_USERNAME}/{repo}"
    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(url, headers=self.headers)
    #     response.raise_for_status()
    #     return response.json()


    async def list_repo_tree(self, repo: str) -> list:
        """
        Получение структуры репозитория.

        Args:
            repo (str): Имя репозитория.

        Returns:
            list: Дерево файлов и папок.
        """
        url = f"{self.base_url}/repos/{MY_GITHUB_USERNAME}/{repo}/contents"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def get_file_content(self, repo: str, path: str) -> dict:
        """
        Получение содержимого файла из репозитория.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к файлу.

        Returns:
            dict: JSON с base64-контентом и SHA.
        """
        url = f"{self.base_url}/repos/{MY_GITHUB_USERNAME}/{repo}/contents/{path}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def create_file(self, repo: str, path: str, filename: str, content: str, message: str) -> dict:
        """
        Создание нового файла в репозитории.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к папке (без ведущего '/').
            filename (str): Имя файла.
            content (str): Текстовое содержимое файла.
            message (str): Сообщение коммита.

        Returns:
            dict: Ответ GitHub API.
        """
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("ascii")
        url_path = f"{path.rstrip('/')}/{filename}" if path else filename
        url = f"{self.base_url}/repos/{MY_GITHUB_USERNAME}/{repo}/contents/{url_path}"
        data = {"message": message, "content": encoded_content}
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def update_file(self, repo: str, path: str, filename: str, content: str, message: str) -> dict:
        """
        Обновление существующего файла в репозитории.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к папке (без ведущего '/').
            filename (str): Имя файла.
            content (str): Новое содержимое файла.
            message (str): Сообщение коммита.

        Returns:
            dict: Ответ GitHub API.
        """
        url_path = f"{path.rstrip('/')}/{filename}" if path else filename
        existing = await self.get_file_content(repo, url_path)
        sha = existing["sha"]
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
        url = f"{self.base_url}/repos/{MY_GITHUB_USERNAME}/{repo}/contents/{url_path}"
        data = {"message": message, "content": encoded, "sha": sha}
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    async def delete_file(self, repo: str, path: str, filename: str, message: str) -> dict:
        """
        Удаление файла из репозитория.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к папке (без ведущего '/').
            filename (str): Имя файла.
            message (str): Сообщение коммита.

        Returns:
            dict: Ответ GitHub API.
        """
        # Формируем относительный путь к файлу в репо
        url_path = f"{path.rstrip('/')}/{filename}" if path else filename

        # Получаем SHA текущего содержимого, необходимый для удаления
        existing = await self.get_file_content(repo, url_path)
        sha = existing["sha"]

        url = f"{self.base_url}/repos/{MY_GITHUB_USERNAME}/{repo}/contents/{url_path}"
        payload = {
            "message": message,
            "sha": sha
        }

        async with httpx.AsyncClient() as client:
            # Для DELETE с телом используем универсальный метод request()
            response = await client.request(
                "DELETE",
                url,
                json=payload,
                headers=self.headers
            )
        response.raise_for_status()
        return response.json()

