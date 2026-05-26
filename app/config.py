from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path.home() / "agenty" / "secrets" / ".env"),
        extra="ignore",
    )

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    langsmith_api_key: str = ""
    langchain_tracing_v2: bool = False

    coding_assistant_database_url: str = ""

    model: str = "gpt-4o"
    max_iterations: int = 3


settings = Settings()
