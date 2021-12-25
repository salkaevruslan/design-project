from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    db_url: str
    secret_key: str

    class Config:
        env_file = ".env"


settings = Settings()


@lru_cache()
def get_settings():
    return {
        "db_url": settings.db_url,
        "secret_key": settings.secret_key
    }
