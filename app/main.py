from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.middleware.rapidapi import RapidAPIMiddleware
from app.middleware.rate_limit import limiter
from app.routers import profile, repositories
from app.services.cache import TTLCache
from app.services.github_api import GitHubAPIClient
from app.services.github_scraper import GitHubScraper


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    app.state.github_api = GitHubAPIClient(app.state.http_client)
    app.state.github_scraper = GitHubScraper(app.state.http_client)
    app.state.cache = TTLCache(default_ttl=settings.cache_ttl)
    yield
    await app.state.http_client.aclose()


tags_metadata = [
    {
        "name": "Profile",
        "description": "Get comprehensive GitHub user profiles including pinned repos, contribution stats, and achievements.",
    },
    {
        "name": "Repositories",
        "description": "Browse and search public repositories for any GitHub user with sorting and pagination.",
    },
    {
        "name": "Health",
        "description": "API health check endpoint.",
    },
]

app = FastAPI(
    title="GitHub Profile Parser API",
    description=(
        "A fast, reliable API for parsing GitHub user profiles and repositories.\n\n"
        "## Features\n"
        "- **Profile data**: Retrieve detailed user info (bio, stats, location, company, etc.)\n"
        "- **Pinned repos**: Get pinned repositories that aren't available via GitHub's REST API\n"
        "- **Contribution stats**: Total contributions in the last year\n"
        "- **Achievement badges**: List of GitHub achievement badges\n"
        "- **Repositories**: Paginated, sortable list of public repos with full metadata\n"
        "- **Caching**: 5-minute TTL cache for fast responses\n\n"
        "## How it works\n"
        "Hybrid approach combining GitHub REST API (structured data) with HTML scraping "
        "(pinned repos, contributions, achievements) to provide the most complete profile data possible."
    ),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.add_middleware(RapidAPIMiddleware)

app.include_router(profile.router, tags=["Profile"])
app.include_router(repositories.router, tags=["Repositories"])


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Returns API health status. Use this to verify the API is running.",
)
async def health_check():
    return {"status": "ok"}
