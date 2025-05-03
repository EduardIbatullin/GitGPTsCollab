# tests/test_endpoints.py

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.domain.models import FileContentResponse, RepoStructureResponse
from app.api.dependencies import get_github_service
from app.domain.services.github_service import GitHubService


# --- Заглушка сервиса для тестов ---
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

    async def create_file(self, repo: str, path: str, filename: str, content: str, message: str) -> FileContentResponse:
        full_path = f"{path}/{filename}" if path else filename
        return FileContentResponse(path=full_path, content=content, encoding="utf-8")


# Переназначаем зависимость
app.dependency_overrides[get_github_service] = lambda: DummyGitHubService()

client = TestClient(app)


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
