"""Environment-backed settings. Loaded lazily (not at import time) so importing this module —
including from tests — never requires the environment to already be configured; only actually
calling a pipeline function that needs a given setting does."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    searxng_url: str
    openrouter_api_key: str
    openrouter_model: str
    serpapi_key: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        searxng_url=os.environ.get("SEARXNG_URL", "http://localhost:8080"),
        openrouter_api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        openrouter_model=os.environ.get("OPENROUTER_MODEL", "dots-studio/dots-3-note-preview:free"),
        # Optional - the search fallback below only fires when this is set.
        serpapi_key=os.environ.get("SERPAPI_KEY", ""),
    )
