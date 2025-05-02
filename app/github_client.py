# app/github_client.py

import base64
from typing import Any, Dict, List
import httpx
from app.config import GITHUB_TOKEN, GITHUB_USERNAME

API_BASE = "https://api.github.com"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

async def get_default_branch(repo: str) -> str:
    url = f"{API_BASE}/repos/{GITHUB_USERNAME}/{repo}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["default_branch"]

async def list_repo_tree(repo: str) -> List[Dict[str, Any]]:
    branch = await get_default_branch(repo)
    url = f"{API_BASE}/repos/{GITHUB_USERNAME}/{repo}/git/trees/{branch}?recursive=1"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("tree", [])

async def get_file_content(repo: str, path: str) -> Dict[str, Any]:
    url = f"{API_BASE}/repos/{GITHUB_USERNAME}/{repo}/contents/{path}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    return {"path": data["path"], "content": content, "encoding": data["encoding"]}

async def create_file(
    repo: str,
    full_path: str,
    content: str,
    message: str = "Create file via API",
) -> Dict[str, Any]:
    url = f"{API_BASE}/repos/{GITHUB_USERNAME}/{repo}/contents/{full_path}"
    b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {"message": message, "content": b64}
    async with httpx.AsyncClient() as client:
        resp = await client.put(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()
