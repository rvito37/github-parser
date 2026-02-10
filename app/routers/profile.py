import asyncio

from fastapi import APIRouter, Request

from app.models.profile import GitHubProfile
from app.services.cache import TTLCache
from app.services.github_api import GitHubAPIClient
from app.services.github_scraper import GitHubScraper

router = APIRouter()


@router.get("/profile/{username}", response_model=GitHubProfile)
async def get_profile(username: str, request: Request):
    cache: TTLCache = request.app.state.cache
    api_client: GitHubAPIClient = request.app.state.github_api
    scraper: GitHubScraper = request.app.state.github_scraper

    cached = cache.get(f"profile:{username}")
    if cached:
        return cached

    api_data, scraped_data = await asyncio.gather(
        api_client.get_user(username),
        scraper.scrape_profile(username),
    )

    profile = GitHubProfile(
        username=api_data["login"],
        name=api_data.get("name"),
        bio=api_data.get("bio"),
        avatar_url=api_data.get("avatar_url"),
        location=api_data.get("location"),
        company=api_data.get("company"),
        blog=api_data.get("blog") or None,
        twitter_username=api_data.get("twitter_username"),
        email=api_data.get("email"),
        public_repos=api_data.get("public_repos", 0),
        public_gists=api_data.get("public_gists", 0),
        followers=api_data.get("followers", 0),
        following=api_data.get("following", 0),
        created_at=api_data.get("created_at"),
        updated_at=api_data.get("updated_at"),
        pinned_repos=scraped_data.get("pinned_repos", []),
        contribution_stats=scraped_data.get("contribution_stats"),
        achievements=scraped_data.get("achievements", []),
    )

    cache.set(f"profile:{username}", profile)
    return profile
