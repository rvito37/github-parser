from pydantic import BaseModel, Field


class PinnedRepo(BaseModel):
    name: str = Field(..., description="Repository name", examples=["linux"])
    description: str | None = Field(None, description="Repository description", examples=["Linux kernel source tree"])
    language: str | None = Field(None, description="Primary programming language", examples=["C"])
    stars: int = Field(0, description="Number of stars", examples=[185000])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "linux",
                    "description": "Linux kernel source tree",
                    "language": "C",
                    "stars": 185000,
                }
            ]
        }
    }


class ContributionStats(BaseModel):
    total_contributions_last_year: int | None = Field(
        None,
        description="Total number of contributions in the last year",
        examples=[2847],
    )


class GitHubProfile(BaseModel):
    username: str = Field(..., description="GitHub username", examples=["torvalds"])
    name: str | None = Field(None, description="Display name", examples=["Linus Torvalds"])
    bio: str | None = Field(None, description="Profile bio")
    avatar_url: str | None = Field(None, description="Avatar image URL", examples=["https://avatars.githubusercontent.com/u/1024025?v=4"])
    location: str | None = Field(None, description="User location", examples=["Portland, OR"])
    company: str | None = Field(None, description="Company or organization", examples=["Linux Foundation"])
    blog: str | None = Field(None, description="Blog or website URL")
    twitter_username: str | None = Field(None, description="Twitter/X username")
    email: str | None = Field(None, description="Public email address")
    public_repos: int = Field(0, description="Number of public repositories", examples=[7])
    public_gists: int = Field(0, description="Number of public gists", examples=[0])
    followers: int = Field(0, description="Number of followers", examples=[228000])
    following: int = Field(0, description="Number of users being followed", examples=[0])
    created_at: str | None = Field(None, description="Account creation date (ISO 8601)", examples=["2011-09-03T15:26:22Z"])
    updated_at: str | None = Field(None, description="Last profile update (ISO 8601)", examples=["2025-01-15T10:30:00Z"])
    pinned_repos: list[PinnedRepo] = Field([], description="Pinned repositories (scraped from profile page)")
    contribution_stats: ContributionStats | None = Field(None, description="Contribution statistics for the last year")
    achievements: list[str] = Field([], description="GitHub achievement badges", examples=[["Arctic Code Vault Contributor", "Pull Shark"]])
