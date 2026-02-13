from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Instagram Clone - Layered Architecture"
    database_url: str = "sqlite+aiosqlite:///./layered.db"
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
