"""Direct page fetch for the deep-dive step — see .docs/SCRAPING_SOURCES.md's "Deep dive" rules:
respect robots.txt, identify the tool with a real User-Agent, rate-limit per domain, skip (don't
fail the whole profile) on any single page's error."""

import asyncio
import time
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "who-is-bot/0.1 (+https://github.com/rafimaliki/who-is; POC, see .docs/SCRAPING_SOURCES.md)"
MIN_SECONDS_BETWEEN_REQUESTS_PER_DOMAIN = 1.0
MAX_TEXT_CHARS = 5000

_last_fetch_at: dict[str, float] = {}
_robots_cache: dict[str, RobotFileParser] = {}


async def _allowed_by_robots(client: httpx.AsyncClient, url: str) -> bool:
    domain = urlparse(url).netloc
    parser = _robots_cache.get(domain)
    if parser is None:
        parser = RobotFileParser()
        try:
            res = await client.get(f"https://{domain}/robots.txt", timeout=5.0)
            parser.parse(res.text.splitlines() if res.status_code == 200 else [])
        except httpx.HTTPError:
            parser.parse([])  # unreachable robots.txt — don't block on it
        _robots_cache[domain] = parser
    return parser.can_fetch(USER_AGENT, url)


async def _respect_rate_limit(domain: str) -> None:
    last = _last_fetch_at.get(domain)
    if last is not None:
        wait = MIN_SECONDS_BETWEEN_REQUESTS_PER_DOMAIN - (time.monotonic() - last)
        if wait > 0:
            await asyncio.sleep(wait)
    _last_fetch_at[domain] = time.monotonic()


async def fetch_text(url: str) -> str | None:
    """Fetches a page and returns its readable text, or None if it should be (or was) skipped."""
    domain = urlparse(url).netloc

    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
        try:
            if not await _allowed_by_robots(client, url):
                return None

            await _respect_rate_limit(domain)
            res = await client.get(url, timeout=10.0)
            res.raise_for_status()
        except httpx.HTTPError:
            return None

    soup = BeautifulSoup(res.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    return text[:MAX_TEXT_CHARS]
