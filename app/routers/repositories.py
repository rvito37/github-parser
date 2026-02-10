from fastapi import APIRouter, Query, Request

from app.models.repository import GitHubRepository, RepositoriesResponse
from app.services.cache import TTLCache
from app.services.github_api import GitHubAPIClient

router = APIRouter()


@router.get("/repos/{username}", response_model=RepositoriesResponse)
async def get_repositories(
    username: str,
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    sort: str = Query("updated", pattern="^(created|updated|pushed|full_name|stars)$"),
):
    cache: TTLCache = request.app.state.cache
    api_client: GitHubAPIClient = request.app.state.github_api

    cache_key = f"repos:{username}:{page}:{per_page}:{sort}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    repos_data = await api_client.get_repos(username, page, per_page, sort)

    repositories = [
        GitHubRepository(
            name=r["name"],
            full_name=r["full_name"],
            description=r.get("description"),
            html_url=r["html_url"],
            language=r.get("language"),
            topics=r.get("topics", []),
            stars=r.get("stargazers_count", 0),
            forks=r.get("forks_count", 0),
            watchers=r.get("watchers_count", 0),
            open_issues=r.get("open_issues_count", 0),
            is_fork=r.get("fork", False),
            is_archived=r.get("archived", False),
            created_at=r.get("created_at"),
            updated_at=r.get("updated_at"),
            pushed_at=r.get("pushed_at"),
        )
        for r in repos_data
    ]

    response = RepositoriesResponse(
        username=username,
        total_count=len(repositories),
        page=page,
        per_page=per_page,
        repositories=repositories,
    )

    cache.set(cache_key, response)
    return response
