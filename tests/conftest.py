import httpx
import pytest

from app.main import app
from app.services.cache import TTLCache
from app.services.github_api import GitHubAPIClient
from app.services.github_scraper import GitHubScraper


@pytest.fixture(autouse=True)
def setup_app_state():
    """Initialize app state that normally comes from lifespan."""
    client = httpx.AsyncClient(timeout=30.0)
    app.state.http_client = client
    app.state.github_api = GitHubAPIClient(client)
    app.state.github_scraper = GitHubScraper(client)
    app.state.cache = TTLCache(default_ttl=300)
    yield
    app.state.cache.clear()
