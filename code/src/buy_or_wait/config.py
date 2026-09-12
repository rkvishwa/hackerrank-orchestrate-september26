from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CODE_ROOT = Path(__file__).resolve().parents[2]


class RecurrencePolicy(BaseSettings):
    min_history: int = 2
    day_tolerance: int = 3
    amount_cv_threshold: float = 0.10
    weekly_days: tuple[int, int] = (5, 9)
    biweekly_days: tuple[int, int] = (12, 16)
    monthly_days: tuple[int, int] = (26, 35)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=CODE_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    repo_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3])
    dataset_dir: Path | None = None
    output_path: Path | None = None
    evidence_cache_dir: Path | None = None
    report_dir: Path | None = None
    # USD per million input/output tokens, keyed by actual model or deployment.
    model_prices: dict[str, tuple[float, float]] = Field(default_factory=dict)

    retrieval_mode: Literal["exact", "hybrid"] = "exact"
    llm_enabled: bool = True
    deterministic_mode: bool = False

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_chat_deployment: str = ""
    azure_vision_deployment: str = ""
    azure_embedding_deployment: str = ""

    database_url: str = "postgresql+psycopg://buyorwait:buyorwait@postgres:5432/buyorwait"
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/1"
    api_key: str = "dev-api-key-change-me"
    azure_max_concurrency: int = 8

    forecast_horizon_days: int = Field(default=90, ge=1)
    recurrence: RecurrencePolicy = Field(default_factory=RecurrencePolicy)

    @property
    def resolved_dataset_dir(self) -> Path:
        return self.dataset_dir or (self.repo_root / "dataset")

    @property
    def resolved_output_path(self) -> Path:
        return self.output_path or (self.repo_root / "output.csv")

    @property
    def resolved_evidence_cache_dir(self) -> Path:
        return self.evidence_cache_dir or (Path(__file__).resolve().parents[2] / "evaluation" / "evidence_cache")

    @property
    def resolved_report_dir(self) -> Path:
        return self.report_dir or CODE_ROOT / "evaluation"


def get_settings() -> Settings:
    return Settings()
