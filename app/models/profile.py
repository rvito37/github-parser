from pydantic import BaseModel


class PinnedRepo(BaseModel):
    name: str
    description: str | None = None
    language: str | None = None
    stars: int = 0


class ContributionStats(BaseModel):
    total_contributions_last_year: int | None = None


class GitHubProfile(BaseModel):
    username: str
    name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None
    location: str | None = None
    company: str | None = None
    blog: str | None = None
    twitter_username: str | None = None
    email: str | None = None
    public_repos: int = 0
    public_gists: int = 0
    followers: int = 0
    following: int = 0
    created_at: str | None = None
    updated_at: str | None = None
    pinned_repos: list[PinnedRepo] = []
    contribution_stats: ContributionStats | None = None
    achievements: list[str] = []
