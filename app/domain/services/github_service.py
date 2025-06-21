# app/domain/services/github_service.py

import base64
import httpx
import hashlib

from app.infrastructure.github_client import GitHubClient
from app.domain.models import FileContentResponse, RepoStructureResponse
from app.core.exceptions import ResourceNotFoundError, GitHubAPIError, InvalidRepositoryError

class GitHubService:
    """
    Сервис для работы с GitHub API.

    Используется для получения структуры репозитория, содержимого файлов,
    создания, обновления и удаления файлов.
    """
    def __init__(self, github_client: GitHubClient):
        """
        Инициализация сервиса GitHub.

        Args:
            github_client (GitHubClient): Экземпляр клиента для работы с GitHub API.
        """
        self.github_client = github_client

    async def get_repo_structure(self, repo: str) -> RepoStructureResponse:
        """
        Получение структуры репозитория на GitHub.

        Args:
            repo (str): Имя репозитория.

        Returns:
            RepoStructureResponse: Модель с именем репозитория и его деревом.
        """
        try:
            tree = await self.github_client.list_repo_tree(repo)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise InvalidRepositoryError(f"Репозиторий '{repo}' не найден")
            raise GitHubAPIError(f"GitHub API error: {e.response.text}", status_code=e.response.status_code)

        return RepoStructureResponse(repo=repo, tree=tree)

    async def get_file_content(self, repo: str, path: str) -> FileContentResponse:
        """
        Получение и декодирование содержимого файла из репозитория.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к файлу.

        Returns:
            FileContentResponse: Содержимое файла и кодировка.
        """
        try:
            api_data = await self.github_client.get_file_content(repo, path)
        except httpx.HTTPStatusError as e:
            # 404: репозиторий или файл не найден
            if e.response.status_code == 404:
                raise ResourceNotFoundError(f"Репозиторий '{repo}' или файл '{path}' не найден")
            # все прочие ошибки GitHub API
            raise GitHubAPIError(
                f"GitHub API error: {e.response.text}",
                status_code=e.response.status_code
            )

        raw_b64 = api_data.get("content", "")
        decoded = base64.b64decode(raw_b64).decode("utf-8")
        return FileContentResponse(
            path=path,
            content=decoded,
            encoding="utf-8"
        )

    async def create_file(
        self,
        repo: str,
        path: str,
        filename: str,
        content: str,
        message: str
    ) -> FileContentResponse:
        """
        Создание нового файла в репозитории.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к папке.
            filename (str): Имя файла.
            content (str): Содержимое файла.
            message (str): Сообщение коммита.

        Returns:
            FileContentResponse: Информация о созданном файле.
        """
        try:
            result = await self.github_client.create_file(repo, path, filename, content, message)
        except httpx.HTTPStatusError as e:
            # 404: репозиторий не найден
            if e.response.status_code == 404:
                raise ResourceNotFoundError(f"Репозиторий '{repo}' или путь '{path}' не найден")
            raise GitHubAPIError(f"GitHub API error: {e.response.text}", status_code=e.response.status_code)

        file_info = result["content"]
        return FileContentResponse(path=file_info["path"], content=content, encoding="utf-8")

    async def update_file(
        self,
        repo: str,
        path: str,
        filename: str,
        content: str,
        message: str,
        content_sha256: str | None = None,
        content_lines: int | None = None
    ) -> FileContentResponse:
        """
        Обновление существующего файла в репозитории.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к папке.
            filename (str): Имя файла.
            content (str): Новое содержимое файла.
            message (str): Сообщение коммита.
            content_sha256 (str | None): Контрольная сумма SHA-256 от содержимого.
            content_lines (int | None): Ожидаемое количество строк.

        Returns:
            FileContentResponse: Информация об обновлённом файле.
        """
        if not content.strip():
            raise ValueError("Передано пустое содержимое файла.")

        if content_sha256:
            actual_hash = hashlib.sha256(content.encode()).hexdigest()
            if actual_hash != content_sha256:
                raise ValueError("Контрольная сумма содержимого не совпадает. Возможна ошибка передачи.")

        if content_lines is not None:
            actual_lines = len(content.splitlines())
            if actual_lines < int(0.8 * content_lines):
                raise ValueError(f"Содержимое файла короче ожидаемого ({actual_lines} < {content_lines})")

        try:
            compile(content, filename, "exec")
        except SyntaxError as e:
            raise ValueError(f"Синтаксическая ошибка в файле: {e}")

        try:
            result = await self.github_client.update_file(repo, path, filename, content, message)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ResourceNotFoundError(f"Файл '{path.rstrip('/')}/{filename}' не найден в репозитории '{repo}'")
            raise GitHubAPIError(f"GitHub API error: {e.response.text}", status_code=e.response.status_code)

        file_info = result["content"]
        return FileContentResponse(path=file_info["path"], content=content, encoding="utf-8")

    async def delete_file(
        self,
        repo: str,
        path: str,
        filename: str,
        message: str
    ) -> FileContentResponse:
        """
        Удаление файла из репозитория.

        Args:
            repo (str): Имя репозитория.
            path (str): Путь к папке.
            filename (str): Имя файла.
            message (str): Сообщение коммита.

        Returns:
            FileContentResponse: Информация об удалённом файле.
        """
        url_path = f"{path.rstrip('/')}/{filename}" if path else filename

        try:
            await self.github_client.delete_file(repo, path, filename, message)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ResourceNotFoundError(f"Файл '{url_path}' не найден в репозитории '{repo}'")
            raise GitHubAPIError(f"GitHub API error: {e.response.text}", status_code=e.response.status_code)

        return FileContentResponse(path=url_path, content="", encoding="utf-8")
