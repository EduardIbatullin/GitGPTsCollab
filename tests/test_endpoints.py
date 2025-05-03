# tests/test_endpoints.py

import pytest
from fastapi.testclient import TestClient
from fastapi import status

from app.api.main import app
from app.api.dependencies import get_github_service
from app.domain.models import FileContentResponse, RepoStructureResponse
from app.core.exceptions import ResourceNotFoundError, InvalidRepositoryError

# --- Сервис-заглушка для успешных сценариев ---
class DummyGitHubService:
    async def get_repo_structure(self, repo: str) -> list:
        return [
            {"path": "", "type": "dir"},
            {"path": "README.md", "type": "file"},
            {"path": "subdir", "type": "dir"},
            {"path": "subdir/nested.txt", "type": "file"},
        ]

    async def get_file_content(self, repo: str, path: str) -> FileContentResponse:
        text = f"Content of {path}"
        return FileContentResponse(path=path, content=text, encoding="utf-8")

    async def create_file(
        self, repo: str, path: str, filename: str, content: str, message: str
    ) -> FileContentResponse:
        full_path = f"{path}/{filename}" if path else filename
        return FileContentResponse(path=full_path, content=content, encoding="utf-8")

    async def update_file(
        self, repo: str, path: str, filename: str, content: str, message: str
    ) -> FileContentResponse:
        full_path = f"{path}/{filename}" if path else filename
        return FileContentResponse(path=full_path, content=content, encoding="utf-8")

    async def delete_file(
        self, repo: str, path: str, filename: str, message: str
    ) -> FileContentResponse:
        full_path = f"{path}/{filename}" if path else filename
        return FileContentResponse(path=full_path, content="", encoding="utf-8")


# --- Сервис-заглушка для ошибок ---
class ErrorGitHubService:
    def __init__(self, exc):
        self.exc = exc

    async def get_repo_structure(self, repo: str):
        raise self.exc

    async def get_file_content(self, repo: str, path: str):
        raise self.exc

    async def create_file(self, repo: str, path: str, filename: str, content: str, message: str):
        raise self.exc

    async def update_file(self, repo: str, path: str, filename: str, content: str, message: str):
        raise self.exc

    async def delete_file(self, repo: str, path: str, filename: str, message: str):
        raise self.exc


# Инициализируем клиент
client = TestClient(app)

# Переназначение зависимости для успешных тестов
app.dependency_overrides[get_github_service] = lambda: DummyGitHubService()


def test_get_repo_structure():
    response = client.get("/repos/test-repo/structure")
    assert response.status_code == 200
    assert response.json() == {
        "repo": "test-repo",
        "tree": [
            {"path": "", "type": "dir"},
            {"path": "README.md", "type": "file"},
            {"path": "subdir", "type": "dir"},
            {"path": "subdir/nested.txt", "type": "file"},
        ],
    }


def test_get_file_content_root():
    response = client.get("/repos/test-repo/file?path=README.md")
    assert response.status_code == 200
    data = response.json()
    assert data["path"] == "README.md"
    assert data["content"] == "Content of README.md"
    assert data["encoding"] == "utf-8"


def test_get_file_content_subfolder():
    response = client.get("/repos/test-repo/file?path=subdir/nested.txt")
    assert response.status_code == 200
    data = response.json()
    assert data["path"] == "subdir/nested.txt"
    assert data["content"] == "Content of subdir/nested.txt"
    assert data["encoding"] == "utf-8"


@pytest.mark.parametrize("path, filename", [
    ("", "root.txt"),
    ("subdir", "nested.txt"),
])
def test_create_file(path, filename):
    payload = {
        "path": path,
        "filename": filename,
        "content": f"Payload for {filename}",
        "message": "Test commit"
    }
    response = client.post("/repos/test-repo/file", json=payload)
    assert response.status_code == 200
    data = response.json()
    expected = filename if path == "" else f"{path}/{filename}"
    assert data["path"] == expected
    assert data["content"] == payload["content"]
    assert data["encoding"] == "utf-8"


@pytest.mark.parametrize("path,filename", [
    ("", "root.txt"),
    ("subdir", "nested.txt"),
])
def test_update_file(path, filename):
    payload = {
        "path": path,
        "filename": filename,
        "content": f"Updated {filename}",
        "message": "Update commit"
    }
    response = client.put("/repos/test-repo/file", json=payload)
    assert response.status_code == 200
    data = response.json()
    expected = filename if path == "" else f"{path}/{filename}"
    assert data["path"] == expected
    assert data["content"] == payload["content"]
    assert data["encoding"] == "utf-8"


@pytest.mark.parametrize("path,filename", [
    ("", "root.txt"),
    ("subdir", "nested.txt"),
])
def test_delete_file(path, filename):
    payload = {
        "path": path,
        "filename": filename,
        "message": "Delete commit"
    }
    # Для DELETE с JSON используем явный .request()
    response = client.request("DELETE", "/repos/test-repo/file", json=payload)
    assert response.status_code == 200
    data = response.json()
    expected = filename if path == "" else f"{path}/{filename}"
    assert data["path"] == expected
    assert data["content"] == ""
    assert data["encoding"] == "utf-8"


# Ошибочные сценарии
@pytest.mark.parametrize("exc,method,endpoint,payload,exp_status,exp_detail", [
    # GET file: репозиторий не найден
    (
        InvalidRepositoryError("Репозиторий 'no-repo' не найден"),
        "GET",
        "/repos/no-repo/file?path=any.txt",
        None,
        status.HTTP_404_NOT_FOUND,
        "Репозиторий 'no-repo' не найден",
    ),
    # GET file: файл не найден
    (
        ResourceNotFoundError("Файл 'nofile.txt' не найден"),
        "GET",
        "/repos/existing-repo/file?path=nofile.txt",
        None,
        status.HTTP_404_NOT_FOUND,
        "Файл 'nofile.txt' не найден",
    ),
    # PUT file: репозиторий не найден
    (
        InvalidRepositoryError("Репозиторий 'no-repo' не найден"),
        "PUT",
        "/repos/no-repo/file",
        {"path": "", "filename": "f.txt", "content": "x", "message": "m"},
        status.HTTP_404_NOT_FOUND,
        "Репозиторий 'no-repo' не найден",
    ),
    # PUT file: файл не найден
    (
        ResourceNotFoundError("Файл 'sub/f.txt' не найден"),
        "PUT",
        "/repos/existing-repo/file",
        {"path": "sub", "filename": "f.txt", "content": "x", "message": "m"},
        status.HTTP_404_NOT_FOUND,
        "Файл 'sub/f.txt' не найден",
    ),
    # DELETE file: репозиторий не найден
    (
        InvalidRepositoryError("Репозиторий 'no-repo' не найден"),
        "DELETE",
        "/repos/no-repo/file",
        {"path": "", "filename": "f.txt", "message": "m"},
        status.HTTP_404_NOT_FOUND,
        "Репозиторий 'no-repo' не найден",
    ),
    # DELETE file: файл не найден
    (
        ResourceNotFoundError("Файл 'sub/f.txt' не найден"),
        "DELETE",
        "/repos/existing-repo/file",
        {"path": "sub", "filename": "f.txt", "message": "m"},
        status.HTTP_404_NOT_FOUND,
        "Файл 'sub/f.txt' не найден",
    ),
])
def test_error_scenarios(exc, method, endpoint, payload, exp_status, exp_detail):
    # Подменяем зависимость на сервис, который сразу бросает нужное исключение
    app.dependency_overrides[get_github_service] = lambda: ErrorGitHubService(exc)

    client = TestClient(app)
    if method == "DELETE" and payload is not None:
        response = client.request(method, endpoint, json=payload)
    elif payload is not None:
        response = getattr(client, method.lower())(endpoint, json=payload)
    else:
        response = getattr(client, method.lower())(endpoint)

    assert response.status_code == exp_status
    assert response.json()["detail"] == exp_detail
