import httpx
from fastapi import HTTPException

from app.config import settings


class GitHubAPIClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        return headers

    async def get_user(self, username: str) -> dict:
        resp = await self._client.get(
            f"{self.BASE_URL}/users/{username}",
            headers=self._headers(),
        )
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found")
        if resp.status_code == 403:
            raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded")
        if resp.status_code >= 500:
            raise HTTPException(status_code=502, detail="GitHub API upstream error")
        resp.raise_for_status()
        return resp.json()

    async def get_repos(
        self,
        username: str,
        page: int = 1,
        per_page: int = 30,
        sort: str = "updated",
    ) -> list[dict]:
        resp = await self._client.get(
            f"{self.BASE_URL}/users/{username}/repos",
            headers=self._headers(),
            params={"page": page, "per_page": per_page, "sort": sort, "direction": "desc"},
        )
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found")
        if resp.status_code == 403:
            raise HTTPException(status_code=429, detail="GitHub API rate limit exceeded")
        if resp.status_code >= 500:
            raise HTTPException(status_code=502, detail="GitHub API upstream error")
        resp.raise_for_status()
        return resp.json()
