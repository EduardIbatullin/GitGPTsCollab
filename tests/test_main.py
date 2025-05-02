# tests/test_main.py

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient

import app.main as main
import app.github_client as gh

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def mock_github(monkeypatch):
    async def fake_list(repo: str):
        return [{"path": "file1.txt", "type": "blob"}]

    async def fake_get(repo: str, path: str):
        return {"path": path, "content": "hello", "encoding": "utf-8"}

    async def fake_create(repo: str, full_path: str, content: str, message: str):
        return {"content": {"path": full_path}, "commit": {"message": message}}

    # Патчим оригинальные функции в github_client
    monkeypatch.setattr(gh, "list_repo_tree", fake_list)
    monkeypatch.setattr(gh, "get_file_content", fake_get)
    monkeypatch.setattr(gh, "create_file", fake_create)

    # И те же имена, уже импортированные в app.main
    monkeypatch.setattr(main, "list_repo_tree", fake_list)
    monkeypatch.setattr(main, "get_file_content", fake_get)
    monkeypatch.setattr(main, "create_file", fake_create)


def test_repo_structure_success():
    resp = client.get("/repos/my-repo/structure")
    assert resp.status_code == 200
    assert resp.json() == {"repo": "my-repo", "tree": [{"path": "file1.txt", "type": "blob"}]}


def test_file_content_success():
    resp = client.get("/repos/my-repo/file", params={"path": "README.md"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["path"] == "README.md"
    assert body["content"] == "hello"
    assert body["encoding"] == "utf-8"


def test_create_file_success():
    payload = {
        "path": "src",
        "filename": "new.txt",
        "content": "data",
        "message": "Add new.txt"
    }
    resp = client.post("/repos/my-repo/file", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["content"]["path"] == "src/new.txt"
    assert body["commit"]["message"] == "Add new.txt"


@pytest.mark.parametrize("payload,missing", [
    ({"filename": "a.txt", "content": "x"}, "path"),
    ({"path": "src", "content": "x"}, "filename"),
    ({"path": "src", "filename": "a.txt"}, "content"),
])
def test_create_file_validation_error(payload, missing):
    resp = client.post("/repos/my-repo/file", json=payload)
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any(err["loc"][-1] == missing for err in errors)
