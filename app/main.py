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


app = FastAPI(
    title="GitHub Profile Parser API",
    description="Parse GitHub user profiles and repositories. Hybrid approach: GitHub REST API + HTML scraping.",
    version="1.0.0",
    lifespan=lifespan,
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


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
