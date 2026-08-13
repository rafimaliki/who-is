"""Thin client for a self-hosted SearXNG instance's JSON search API — see
.docs/SCRAPING_SOURCES.md for why SearXNG over a paid search API."""

import httpx

from app.config import get_settings

from .types import SearxResult

# SearXNG's inherited default engine catalog fans a query out to ~60 general-category engines at
# once - every one of our own queries was really 60 outbound requests, which is what tripped
# rate limits/CAPTCHAs this fast regardless of caching. Restricting to a small, reliable set here
# (rather than trimming the shared instance-wide catalog in searxng/settings.yml) keeps SearXNG's
# own web UI unrestricted for manual use while fixing it for what this backend actually calls.
ENGINES = "bing,wikipedia,mojeek"


async def search(query: str, count: int = 10) -> list[SearxResult]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(
            f"{settings.searxng_url}/search",
            params={"q": query, "format": "json", "engines": ENGINES},
        )
        res.raise_for_status()
        data = res.json()

    return [
        SearxResult(title=item.get("title", ""), url=item.get("url", ""), content=item.get("content", ""))
        for item in data.get("results", [])[:count]
    ]
