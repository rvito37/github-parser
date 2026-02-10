from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_token: str = ""
    rapidapi_proxy_secret: str = ""
    cache_ttl: int = 300
    rate_limit: str = "30/minute"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
