from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):

    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    google_api_key: str | None = None

    tavily_api_key: str | None = None

    groq_api_key: str | None = None
    groq_model: str | None = None
    groq_fast: str | None = None

    langsmith_tracing: str | None = None
    langsmith_endpoint: str | None = None
    langsmith_api_key: str | None = None
    langsmith_project: str | None = None

    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()