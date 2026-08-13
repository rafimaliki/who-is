"""Thin client for a self-hosted SearXNG instance's JSON search API — see
.docs/SCRAPING_SOURCES.md for why SearXNG over a paid search API."""

import httpx

from app.config import get_settings

from .types import SearxResult


async def search(query: str, count: int = 10) -> list[SearxResult]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(
            f"{settings.searxng_url}/search",
            params={"q": query, "format": "json"},
        )
        res.raise_for_status()
        data = res.json()

    return [
        SearxResult(title=item.get("title", ""), url=item.get("url", ""), content=item.get("content", ""))
        for item in data.get("results", [])[:count]
    ]
