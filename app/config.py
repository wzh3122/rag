from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    frontend_cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
    )

    enable_auth: bool = False
    api_auth_token: str = "change_me"

    enable_rate_limit: bool = True
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60

    database_url: str = "sqlite:///./data/legal_agent_rag.db"

    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    llm_timeout_seconds: int = 60

    embedding_provider: str = "mock"
    embedding_api_key: str = ""
    embedding_base_url: str = ""
    embedding_model: str = "mock-embedding"
    embedding_dimension: int = 1024
    embedding_timeout_seconds: int = 60

    reranker_provider: str = "mock"
    reranker_api_key: str = ""
    reranker_base_url: str = ""
    reranker_model: str = "mock-reranker"
    reranker_timeout_seconds: int = 60

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "legal_articles_dev"

    opensearch_url: str = "http://localhost:9200"
    opensearch_username: str = "admin"
    opensearch_password: str = "admin"
    opensearch_index: str = "legal_articles_keyword_dev"

    rag_index_ready: bool = False
    rag_strict_mode: bool = True
    max_retry_times: int = 2

    enable_agent_trace: bool = True
    trace_save_raw_input: bool = False
    trace_save_raw_output: bool = False
    trace_max_text_length: int = 1000

    save_chat_history: bool = True
    save_chat_history_in_production: bool = False
    save_accumulated_facts: bool = True

    run_integration_tests: bool = False

    @field_validator("frontend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value  # type: ignore[return-value]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def should_save_chat_history(self) -> bool:
        if self.is_production:
            return self.save_chat_history_in_production
        return self.save_chat_history


@lru_cache
def get_settings() -> Settings:
    return Settings()

