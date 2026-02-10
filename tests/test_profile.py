from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def mock_github_user():
    return {
        "login": "testuser",
        "name": "Test User",
        "bio": "Developer",
        "avatar_url": "https://avatars.githubusercontent.com/u/123",
        "location": "Earth",
        "company": "TestCorp",
        "blog": "https://test.com",
        "twitter_username": "testuser",
        "email": None,
        "public_repos": 10,
        "public_gists": 2,
        "followers": 100,
        "following": 50,
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.mark.asyncio
async def test_get_profile(mock_github_user):
    with (
        patch("app.services.github_api.GitHubAPIClient.get_user", new_callable=AsyncMock) as mock_api,
        patch("app.services.github_scraper.GitHubScraper.scrape_profile", new_callable=AsyncMock) as mock_scraper,
    ):
        mock_api.return_value = mock_github_user
        mock_scraper.return_value = {
            "pinned_repos": [],
            "contribution_stats": None,
            "achievements": [],
        }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/profile/testuser")

        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["name"] == "Test User"
        assert data["followers"] == 100
        assert data["public_repos"] == 10


@pytest.mark.asyncio
async def test_profile_not_found():
    with patch(
        "app.services.github_api.GitHubAPIClient.get_user",
        new_callable=AsyncMock,
        side_effect=HTTPException(status_code=404, detail="GitHub user 'nonexistentuser12345' not found"),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/profile/nonexistentuser12345")

        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"]
