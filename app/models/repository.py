from pydantic import BaseModel


class GitHubRepository(BaseModel):
    name: str
    full_name: str
    description: str | None = None
    html_url: str
    language: str | None = None
    topics: list[str] = []
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    is_fork: bool = False
    is_archived: bool = False
    created_at: str | None = None
    updated_at: str | None = None
    pushed_at: str | None = None


class RepositoriesResponse(BaseModel):
    username: str
    total_count: int
    page: int
    per_page: int
    repositories: list[GitHubRepository]
