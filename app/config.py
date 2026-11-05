from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, read from environment variables or a .env file."""

    database_url: str = "sqlite:///./temperature.db"
    api_key: str = "dev-secret-key"  # change in production via the API_KEY env var
    seed_on_startup: bool = True

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
