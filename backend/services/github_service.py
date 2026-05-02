import re
from datetime import datetime, timezone, timedelta

import httpx
from fastapi import HTTPException


class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self._cache = {}
        self._ttl = timedelta(minutes=10)

    def parse_github_url(self, url: str):
        match = re.match(r"^https?://github\.com/([^/]+)/([^/]+?)/?$", url.strip())
        if not match:
            raise ValueError("Invalid GitHub repository URL. Use format https://github.com/owner/repo")
        return match.group(1), match.group(2)

    async def _get(self, path: str):
        now = datetime.now(timezone.utc)
        if path in self._cache and now - self._cache[path][0] < self._ttl:
            return self._cache[path][1]

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.BASE_URL}{path}", headers={"Accept": "application/vnd.github+json"})

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Repository not found or private repository")
        if response.status_code == 403:
            raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded")
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        self._cache[path] = (now, data)
        return data

    async def get_repo(self, owner: str, repo: str):
        return await self._get(f"/repos/{owner}/{repo}")

    async def get_languages(self, owner: str, repo: str):
        return await self._get(f"/repos/{owner}/{repo}/languages")

    async def get_tree(self, owner: str, repo: str, branch: str):
        ref_data = await self._get(f"/repos/{owner}/{repo}/git/trees/{branch}?recursive=1")
        return ref_data.get("tree", [])

    async def get_commits(self, owner: str, repo: str):
        return await self._get(f"/repos/{owner}/{repo}/commits?per_page=5")
