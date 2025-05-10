import pytest
from app.domain.services.github_service import GitHubService
from app.core.exceptions import GitHubAPIError

import hashlib


class DummyGitHubClient:
    async def update_file(self, repo, path, filename, content, message):
        return {"content": {"path": f"{path}/{filename}"}}


@pytest.mark.asyncio
async def test_valid_update():
    service = GitHubService(github_client=DummyGitHubClient())
    content = "print('Hello')\nprint('World')"
    sha = hashlib.sha256(content.encode()).hexdigest()
    result = await service.update_file(
        repo="test-repo",
        path="src",
        filename="main.py",
        content=content,
        message="update",
        content_sha256=sha,
        content_lines=2,
    )
    assert result.path == "src/main.py"


@pytest.mark.asyncio
async def test_invalid_hash():
    service = GitHubService(github_client=DummyGitHubClient())
    content = "print('broken hash')"
    with pytest.raises(ValueError, match="Контрольная сумма содержимого не совпадает"):
        await service.update_file(
            repo="r",
            path="",
            filename="f.py",
            content=content,
            message="msg",
            content_sha256="invalid",
            content_lines=1,
        )


@pytest.mark.asyncio
async def test_short_content():
    service = GitHubService(github_client=DummyGitHubClient())
    content = "x = 1"
    lines_expected = 10
    with pytest.raises(ValueError, match="короче ожидаемого"):
        await service.update_file(
            repo="r",
            path="",
            filename="f.py",
            content=content,
            message="msg",
            content_lines=lines_expected,
        )


@pytest.mark.asyncio
async def test_syntax_error():
    service = GitHubService(github_client=DummyGitHubClient())
    content = "def broken(\n"
    with pytest.raises(ValueError, match="Синтаксическая ошибка"):
        await service.update_file(
            repo="r",
            path="",
            filename="bad.py",
            content=content,
            message="msg",
        )