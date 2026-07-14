"""Application settings via pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    workflow_manifest_path: str = "workflow_manifest.json"
    agent_library_root: str = "agent_library"

    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2024-02-15-preview"

    hitl_auto_approve: bool = True
    dry_run: bool = False

    @property
    def llm_available(self) -> bool:
        return bool(
            self.azure_openai_endpoint
            and self.azure_openai_api_key
            and self.azure_openai_deployment
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
