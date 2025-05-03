# app/api/dependencies.py

from fastapi import Depends
from app.infrastructure.github_client import GitHubClient
from app.domain.services.github_service import GitHubService

def get_github_client() -> GitHubClient:
    """
    Функция для инъекции зависимости GitHub клиента.
    
    Возвращает экземпляр GitHubClient, который используется для взаимодействия
    с API GitHub.

    Returns:
        GitHubClient: Экземпляр клиента для работы с GitHub API.
    """
    return GitHubClient()

def get_github_service(
    client: GitHubClient = Depends(get_github_client),
) -> GitHubService:
    """
    Функция для инъекции зависимости GitHub сервиса.
    
    Оборачивает GitHubClient в GitHubService, инкапсулирующий бизнес-логику.

    Returns:
        GitHubService: Экземпляр сервиса для работы с GitHub API.
    """
    return GitHubService(client)
