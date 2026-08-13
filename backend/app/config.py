"""Environment-backed settings. Loaded lazily (not at import time) so importing this module —
including from tests — never requires the environment to already be configured; only actually
calling a pipeline function that needs a given setting does."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    searxng_url: str
    gemini_api_key: str
    gemini_model: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        searxng_url=os.environ.get("SEARXNG_URL", "http://localhost:8080"),
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        gemini_model=os.environ.get("GEMINI_MODEL", "gemini-flash-latest"),
    )
