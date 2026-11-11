from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str | None = None
    database_url: str = "postgresql+asyncpg://kad:kad_dev_password@localhost:5432/kad"
    redis_url: str = "redis://localhost:6379/0"
    max_inns_per_user: int = 50
    default_timezone: str = "Europe/Moscow"
    kad_provider: str = "disabled"


settings = Settings()
