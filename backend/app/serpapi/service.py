"""Thin client for SerpAPI's Google-results JSON API — the paid fallback used by app/search
when the self-hosted SearXNG instance comes back empty or blocked.
Reuses SearxResult (title/url/content) rather than defining an identical shape here."""

import httpx

from app.config import get_settings
from app.searxng.types import SearxResult

SERPAPI_URL = "https://serpapi.com/search"


async def search(query: str, count: int = 10) -> list[SearxResult]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(
            SERPAPI_URL,
            params={"q": query, "engine": "google", "api_key": settings.serpapi_key, "num": count},
        )
        res.raise_for_status()
        data = res.json()

    return [
        SearxResult(title=item.get("title", ""), url=item.get("link", ""), content=item.get("snippet", ""))
        for item in data.get("organic_results", [])[:count]
    ]
