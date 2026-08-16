"""Real search -> cluster -> deep dive -> extract pipeline. See .docs/LLM_PIPELINE.md for the
design this implements."""

import asyncio
import uuid
from collections.abc import Awaitable
from typing import TypeVar

from fastapi import HTTPException

from app.config import get_settings
from app.llm import service as llm
from app.profile.types import ProfileResponse
from app.scraping import service as scraping
from app.serpapi import service as serpapi
from app.searxng import service as searxng
from app.searxng.types import SearxResult
from app.shared.store import StoredCandidate, store
from app.shared.types import Education, ProfileFields, SocialProfile, Source

from . import queries
from .types import Candidate, SearchResponse

MAX_DEEP_DIVE_PAGES = 4

# How many ranked results reach the clustering LLM. Past this it's mostly long-tail noise, and the
# prompt gets long enough to hurt clustering quality.
MAX_CLUSTER_RESULTS = 20

T = TypeVar("T")


def _candidate_name(label: str) -> str:
    """`label` is "Name, occupation, city" — just the name, for a fallback query."""
    return label.split(",")[0].strip()


def _names_overlap(expected: str, actual: str) -> bool:
    """Whether `actual` plausibly names the same person as `expected`.

    Sharing one common given name is not enough — "Ahmad Rafi Maliki" vs "Ahmad Fauzi" is a
    different person. Two shared tokens is the normal bar; a single shared *surname* also passes,
    so "Marie Curie" still matches "Maria Salomea Skłodowska-Curie".

    ponytail: token overlap, not real entity resolution. It catches outright identity drift (the
    deep dive latching onto a same-name-different-person page); it won't catch a transliteration
    sharing no tokens at all. Swap in proper fuzzy matching only if that shows up in practice.
    """
    expected_tokens = queries.name_tokens(expected)
    actual_tokens = set(queries.name_tokens(actual))
    if not expected_tokens or not actual_tokens:
        return False

    shared = [t for t in expected_tokens if t in actual_tokens]
    if len(shared) >= 2 or len(expected_tokens) == 1:
        return bool(shared)
    # A lone shared token only counts when it's a distinctive surname, never the given name.
    return shared == expected_tokens[-1:] and len(expected_tokens[-1]) >= 5


async def _search(query: str, count: int) -> list[SearxResult]:
    """SerpAPI (real Google results) when a key is configured, SearXNG otherwise.

    SerpAPI is primary rather than a fallback because the self-hosted SearXNG engines silently drop
    "exact phrase" quoting and site: operators — for a low-profile person that turns every query
    into a first-name match and buries them under famous namesakes. SearXNG stays the free path
    when no key is set, and the fallback when SerpAPI errors.
    """
    if not get_settings().serpapi_key:
        return await searxng.search(query, count=count)

    try:
        results = await serpapi.search(query, count=count)
    except Exception:  # noqa: BLE001 - a free fallback exists, so try it before surfacing an error
        results = []
    return results or await searxng.search(query, count=count)


async def _search_many(query_list: list[str], count: int) -> list[SearxResult]:
    """Runs the query set concurrently and merges results, first-seen URL wins.

    Concurrent because these are independent network calls on a synchronous request path — running
    four in sequence multiplies the user's wait for no benefit.
    """
    batches = await asyncio.gather(*(_search(q, count=count) for q in query_list), return_exceptions=True)

    merged: dict[str, SearxResult] = {}
    errors: list[BaseException] = []
    for batch in batches:
        if isinstance(batch, BaseException):
            errors.append(batch)
            continue
        for result in batch:
            merged.setdefault(result.url, result)

    if not merged and errors:
        raise errors[0]  # every query failed - surface it rather than reporting "nobody found"
    return list(merged.values())


async def _upstream(awaitable: Awaitable[T]) -> T:
    """Runs a SearXNG/OpenRouter call, translating any failure into the documented error shape
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
    all_results = await _upstream(_search_many(queries.build(name, filters), count=10))

    if not all_results:
        return SearchResponse(search_id=f"s_{uuid.uuid4().hex[:8]}", candidates=[], auto_selected=False)

    # Rank before clustering: a result missing a name token is about someone else, and letting it
    # through means the LLM clusters famous namesakes instead of the person actually asked for.
    result_tuples = queries.rank(
        name, [(r.url, r.title, r.content) for r in all_results], limit=MAX_CLUSTER_RESULTS
    )
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

    # match.label carries the disambiguators (name, occupation, city); the expanded query set adds
    # the exact-phrase and handle searches that actually surface a low-profile person's own pages.
    expected_name = _candidate_name(match.label)
    deep_dive_queries = [match.label, *queries.build(expected_name, {})]
    results = queries.rank(
        expected_name,
        [(r.url, r.title, r.content) for r in await _upstream(_search_many(deep_dive_queries, count=10))],
        limit=MAX_DEEP_DIVE_PAGES,
    )
    # Clustering already proved these URLs are about this candidate, so they're worth fetching
    # alongside the fresh search hits rather than only as a last resort.
    for url in match.source_urls:
        if len(results) >= MAX_DEEP_DIVE_PAGES + 2:
            break
        if all(url != existing_url for existing_url, _, _ in results):
            results.append((url, url, ""))

    pages: list[tuple[str, str, str]] = []
    photos: list[tuple[str, str]] = []  # (image_url, page it came from)
    for url, title, snippet in results:
        page = await scraping.fetch_page(url)
        # Direct fetch is best-effort (robots.txt, bot-blocking, timeouts all skip silently per
        # app/scraping/service.py) - fall back to the search snippet rather than losing the page.
        text, image = page if page else (None, None)
        if not text and not snippet:
            continue
        pages.append((url, title, text or snippet))
        if image:
            photos.append((image, url))

    if not pages:
        raise HTTPException(
            502, detail={"error": "upstream_error", "message": "no reachable pages for the chosen candidate"}
        )

    extracted = await _upstream(llm.extract_profile(match.label, match.summary, pages))

    # Deep-dive pages can drift onto a same-name-different-person page (a common surname, a stale
    # fallback source) - catch it here rather than silently showing the wrong person's profile.
    extracted_names = [extracted.fields.full_name, *extracted.fields.aliases]
    if not any(_names_overlap(expected_name, n) for n in extracted_names):
        raise HTTPException(
            502,
            detail={
                "error": "upstream_error",
                "message": "extracted profile name doesn't match the selected candidate",
            },
        )

    # Photos come from the pages themselves (og:image), not from the LLM: a scraped preview image
    # has a real page behind it by construction, which is what the no-field-without-a-source rule
    # actually asks for. The LLM's own photo guesses are kept but come second.
    all_photos = list(dict.fromkeys([*(image for image, _ in photos), *extracted.fields.photos]))
    photo_sources = [
        Source(url=page_url, title=page_url, snippet=image, supports_field="photos") for image, page_url in photos
    ]

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
            photos=all_photos,
            summary=extracted.fields.summary,
        ),
        sources=[*(Source(**s.model_dump()) for s in extracted.sources), *photo_sources],
    )
    store.profiles[profile_id] = profile
    return profile
