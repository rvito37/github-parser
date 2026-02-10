from pydantic import BaseModel, Field


class GitHubRepository(BaseModel):
    name: str = Field(..., description="Repository name", examples=["linux"])
    full_name: str = Field(..., description="Full repository name (owner/repo)", examples=["torvalds/linux"])
    description: str | None = Field(None, description="Repository description", examples=["Linux kernel source tree"])
    html_url: str = Field(..., description="URL to repository on GitHub", examples=["https://github.com/torvalds/linux"])
    language: str | None = Field(None, description="Primary programming language", examples=["C"])
    topics: list[str] = Field([], description="Repository topics/tags", examples=[["kernel", "linux", "operating-system"]])
    stars: int = Field(0, description="Number of stars", examples=[185000])
    forks: int = Field(0, description="Number of forks", examples=[55000])
    watchers: int = Field(0, description="Number of watchers", examples=[185000])
    open_issues: int = Field(0, description="Number of open issues", examples=[350])
    is_fork: bool = Field(False, description="Whether the repo is a fork")
    is_archived: bool = Field(False, description="Whether the repo is archived")
    created_at: str | None = Field(None, description="Creation date (ISO 8601)", examples=["2011-09-04T22:48:12Z"])
    updated_at: str | None = Field(None, description="Last update date (ISO 8601)", examples=["2025-01-20T12:00:00Z"])
    pushed_at: str | None = Field(None, description="Last push date (ISO 8601)", examples=["2025-01-20T11:55:00Z"])


class RepositoriesResponse(BaseModel):
    username: str = Field(..., description="GitHub username", examples=["torvalds"])
    total_count: int = Field(..., description="Number of repositories returned in this page", examples=[7])
    page: int = Field(..., description="Current page number", examples=[1])
    per_page: int = Field(..., description="Items per page", examples=[30])
    repositories: list[GitHubRepository] = Field(..., description="List of repositories")
