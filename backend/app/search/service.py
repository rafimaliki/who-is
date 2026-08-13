"""Real search -> cluster -> deep dive -> extract pipeline. See .docs/LLM_PIPELINE.md and
.docs/SCRAPING_SOURCES.md for the design this implements."""

import uuid
from collections.abc import Awaitable
from typing import TypeVar

from fastapi import HTTPException

from app.llm import service as llm
from app.profile.types import ProfileResponse
from app.scraping import service as scraping
from app.searxng import service as searxng
from app.shared.store import StoredCandidate, store
from app.shared.types import Education, ProfileFields, SocialProfile, Source

from .types import Candidate, SearchResponse

MAX_DEEP_DIVE_PAGES = 4

# Per .docs/SCRAPING_SOURCES.md's social media discovery design: site: operators through the same
# search provider, never platform-specific scraping.
SOCIAL_SITES = ["instagram.com", "facebook.com", "x.com", "twitter.com", "linkedin.com", "tiktok.com", "youtube.com"]

T = TypeVar("T")


def _build_query(name: str, filters: dict[str, object]) -> str:
    parts = [name]
    for key in ("country", "age_range", "occupation"):
        value = filters.get(key)
        if value:
            parts.append(str(value))
    aliases = filters.get("aliases")
    if aliases:
        parts.extend(str(a) for a in aliases)
    return " ".join(parts)


def _candidate_name(label: str) -> str:
    """`label` is "Name, occupation, city" — just the name, for a fallback query."""
    return label.split(",")[0].strip()


async def _upstream(awaitable: Awaitable[T]) -> T:
    """Runs a SearXNG/Gemini call, translating any failure into the documented error shape
    instead of letting a raw exception (with library/stack-trace detail) escape to the client."""
    try:
        return await awaitable
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 - deliberately broad: any upstream failure maps the same way
        message = str(exc)
        if "429" in message or "RESOURCE_EXHAUSTED" in message.upper():
            raise HTTPException(status_code=429, detail={"error": "rate_limited", "message": message}) from exc
        raise HTTPException(status_code=502, detail={"error": "upstream_error", "message": message}) from exc


async def run_search(name: str, filters: dict[str, object]) -> SearchResponse:
    query = _build_query(name, filters)
    social_query = f"{query} (" + " OR ".join(f"site:{s}" for s in SOCIAL_SITES) + ")"

    broad = await _upstream(searxng.search(query, count=10))
    social = await _upstream(searxng.search(social_query, count=6))
    all_results = broad + social

    if not all_results:
        return SearchResponse(search_id=f"s_{uuid.uuid4().hex[:8]}", candidates=[], auto_selected=False)

    result_tuples = [(r.url, r.title, r.content) for r in all_results]
    cluster_filters = {k: v for k, v in filters.items() if v}
    clustered = await _upstream(llm.cluster_candidates(name, cluster_filters, result_tuples))

    if not clustered.candidates:
        return SearchResponse(search_id=f"s_{uuid.uuid4().hex[:8]}", candidates=[], auto_selected=False)

    stored: list[StoredCandidate] = []
    api_candidates: list[Candidate] = []
    for c in clustered.candidates:
        api_candidate = Candidate(
            id=f"c_{uuid.uuid4().hex[:8]}", label=c.label, summary=c.summary, photo_url=c.photo_url, confidence=c.confidence
        )
        api_candidates.append(api_candidate)
        stored.append(StoredCandidate(candidate=api_candidate, label=c.label, summary=c.summary, source_urls=c.source_urls))

    search_id = f"s_{uuid.uuid4().hex[:8]}"
    store.searches[search_id] = stored

    return SearchResponse(search_id=search_id, candidates=api_candidates, auto_selected=len(api_candidates) == 1)


async def run_select(search_id: str, candidate_id: str) -> ProfileResponse:
    stored_candidates = store.searches.get(search_id)
    if stored_candidates is None:
        raise HTTPException(404, detail={"error": "not_found", "message": "search_id does not exist"})

    match = next((sc for sc in stored_candidates if sc.candidate.id == candidate_id), None)
    if match is None:
        raise HTTPException(
            404, detail={"error": "not_found", "message": "candidate_id does not exist for this search"}
        )

    # match.label already carries the disambiguators (name, occupation, city) SCRAPING_SOURCES.md
    # calls for - match.summary is a full sentence, not query material; appending it just made
    # the query long and redundant enough that SearXNG's engines sometimes matched nothing at all.
    results = await _upstream(searxng.search(match.label, count=MAX_DEEP_DIVE_PAGES))
    if not results:
        # Rare (a less-documented person), but the disambiguated query can still come up empty -
        # retry with just the name before giving up on the whole profile.
        fallback_query = _candidate_name(match.label)
        if fallback_query and fallback_query != match.label:
            results = await _upstream(searxng.search(fallback_query, count=MAX_DEEP_DIVE_PAGES))

    pages: list[tuple[str, str, str]] = []
    for r in results:
        text = await scraping.fetch_text(r.url)
        # Direct fetch is best-effort (robots.txt, bot-blocking, timeouts all skip silently per
        # .docs/SCRAPING_SOURCES.md) - fall back to the search snippet rather than losing the page.
        pages.append((r.url, r.title, text or r.content))

    if not pages:
        # Both scoped queries came up empty — can happen even for an easily-searchable person if
        # every SearXNG engine is currently rate-limited/blocked, not just for an obscure one.
        # Fall back to the URLs that already grounded this candidate during clustering rather than
        # failing the whole profile when we already have public pages for them.
        for url in match.source_urls[:MAX_DEEP_DIVE_PAGES]:
            text = await scraping.fetch_text(url)
            if text:
                pages.append((url, url, text))

    if not pages:
        raise HTTPException(
            502, detail={"error": "upstream_error", "message": "no reachable pages for the chosen candidate"}
        )

    extracted = await _upstream(llm.extract_profile(match.label, match.summary, pages))

    profile_id = f"p_{uuid.uuid4().hex[:8]}"
    profile = ProfileResponse(
        profile_id=profile_id,
        fields=ProfileFields(
            full_name=extracted.fields.full_name,
            aliases=extracted.fields.aliases,
            location_current=extracted.fields.location_current,
            location_history=extracted.fields.location_history,
            occupation=extracted.fields.occupation,
            employer=extracted.fields.employer,
            education=[Education(**e.model_dump()) for e in extracted.fields.education],
            social_profiles=[SocialProfile(**s.model_dump()) for s in extracted.fields.social_profiles],
            photos=extracted.fields.photos,
            summary=extracted.fields.summary,
        ),
        sources=[Source(**s.model_dump()) for s in extracted.sources],
    )
    store.profiles[profile_id] = profile
    return profile
