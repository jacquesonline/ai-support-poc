from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ai_provider: str = "fake"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4-mini"
    model_input_cost_per_million_aud: float | None = None
    model_output_cost_per_million_aud: float | None = None
    experiment_spend_cap_aud: float = 25.0
    experiment_model_call_cap: int = 12
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
