# app/api/routers/repo_router.py

from fastapi import APIRouter, Depends
from app.domain.services.github_service import GitHubService
from app.domain.models import (
    RepoStructureResponse,
    FileContentResponse,
    CreateFileRequest,
    UpdateFileRequest,
    DeleteFileRequest,
)
from app.api.dependencies import get_github_service

router = APIRouter()

@router.get("/repos/{repo}/structure", response_model=RepoStructureResponse)
async def get_repo_structure(
    repo: str, 
    github_service: GitHubService = Depends(get_github_service)
) -> RepoStructureResponse:
    """
    Эндпоинт для получения структуры репозитория на GitHub.

    Args:
        repo (str): Имя репозитория на GitHub.
        github_service (GitHubService): Сервис для взаимодействия с GitHub API.

    Returns:
        RepoStructureResponse: Ответ с информацией о структуре репозитория.
    """
    structure = await github_service.get_repo_structure(repo)
    return RepoStructureResponse(repo=repo, tree=structure)

@router.get("/repos/{repo}/file", response_model=FileContentResponse)
async def get_file_content(
    repo: str, 
    path: str, 
    github_service: GitHubService = Depends(get_github_service)
) -> FileContentResponse:
    """
    Эндпоинт для получения содержимого файла из репозитория на GitHub.

    Args:
        repo (str): Имя репозитория.
        path (str): Путь к файлу в репозитории.
        github_service (GitHubService): Сервис для взаимодействия с GitHub API.

    Returns:
        FileContentResponse: Ответ с содержимым файла.
    """
    return await github_service.get_file_content(repo, path)

@router.post("/repos/{repo}/file", response_model=FileContentResponse)
async def create_new_file(
    repo: str, 
    file_data: CreateFileRequest, 
    github_service: GitHubService = Depends(get_github_service)
) -> FileContentResponse:
    """
    Эндпоинт для создания нового файла в репозитории на GitHub.

    Args:
        repo (str): Имя репозитория.
        file_data (CreateFileRequest): Данные для создания нового файла.
        github_service (GitHubService): Сервис для взаимодействия с GitHub API.

    Returns:
        FileContentResponse: Ответ с информацией о созданном файле.
    """
    return await github_service.create_file(
        repo,
        file_data.path,
        file_data.filename,
        file_data.content,
        file_data.message,
    )

@router.put("/repos/{repo}/file", response_model=FileContentResponse)
async def update_file(
    repo: str,
    file_data: UpdateFileRequest,
    github_service: GitHubService = Depends(get_github_service)
) -> FileContentResponse:
    """
    Эндпоинт для обновления существующего файла в репозитории на GitHub.

    Args:
        repo (str): Имя репозитория.
        file_data (UpdateFileRequest): Данные для обновления файла.
        github_service (GitHubService): Сервис для взаимодействия с GitHub API.

    Returns:
        FileContentResponse: Ответ с информацией об обновлённом файле.
    """
    return await github_service.update_file(
        repo,
        file_data.path,
        file_data.filename,
        file_data.content,
        file_data.message,
    )

@router.delete("/repos/{repo}/file", response_model=FileContentResponse)
async def delete_file(
    repo: str,
    file_data: DeleteFileRequest,
    github_service: GitHubService = Depends(get_github_service)
) -> FileContentResponse:
    """
    Эндпоинт для удаления файла из репозитория на GitHub.

    Args:
        repo (str): Имя репозитория.
        file_data (DeleteFileRequest): Данные для удаления файла.
        github_service (GitHubService): Сервис для взаимодействия с GitHub API.

    Returns:
        FileContentResponse: Ответ с информацией об удалённом файле.
    """
    return await github_service.delete_file(
        repo,
        file_data.path,
        file_data.filename,
        file_data.message,
    )
