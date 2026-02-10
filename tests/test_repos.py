from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def mock_repos():
    return [
        {
            "name": "my-project",
            "full_name": "testuser/my-project",
            "description": "A test project",
            "html_url": "https://github.com/testuser/my-project",
            "language": "Python",
            "topics": ["api", "fastapi"],
            "stargazers_count": 42,
            "forks_count": 5,
            "watchers_count": 42,
            "open_issues_count": 3,
            "fork": False,
            "archived": False,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2024-06-01T00:00:00Z",
            "pushed_at": "2024-06-01T00:00:00Z",
        }
    ]


@pytest.mark.asyncio
async def test_get_repos(mock_repos):
    with patch(
        "app.services.github_api.GitHubAPIClient.get_repos",
        new_callable=AsyncMock,
        return_value=mock_repos,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/repos/testuser?page=1&per_page=10&sort=updated")

        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["total_count"] == 1
        assert data["repositories"][0]["name"] == "my-project"
        assert data["repositories"][0]["stars"] == 42


@pytest.mark.asyncio
async def test_repos_pagination_params():
    with patch(
        "app.services.github_api.GitHubAPIClient.get_repos",
        new_callable=AsyncMock,
        return_value=[],
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/repos/testuser?page=2&per_page=5&sort=stars")

        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 2
        assert data["per_page"] == 5
        assert data["repositories"] == []
