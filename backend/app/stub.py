"""Stub implementation of the search/select pipeline — fixture data + fake latency standing in
for the real search -> cluster -> deep dive -> extract pipeline (see docs/LLM_PIPELINE.md and
docs/SCRAPING_SOURCES.md for what that becomes). Ported from the frontend's former
mockApi.ts — same trigger words, same randomized-outcome logic, same fixtures, now the one
source of truth instead of duplicated client-side.

Swapping in the real pipeline later means replacing the bodies of `run_search` and `run_select`
only — the route handlers and response shapes stay identical.
"""

import asyncio
import random
import uuid
from dataclasses import dataclass, field

from fastapi import HTTPException

from .models import Candidate, Education, ProfileFields, ProfileResponse, SearchResponse, SocialProfile, Source

# Demo pacing, not simulated real latency — long enough for the frontend's rotating
# "thinking" message list to actually cycle a few times.
SEARCH_DELAY_S = 4.0
SELECT_DELAY_S = 6.0

DEV_TRIGGERS = {
    "ambiguous": "john smith",
    "empty": "test empty",
    "error": "test error",
}

OCCUPATIONS = [
    "software engineer",
    "attorney",
    "high school teacher",
    "restaurant owner",
    "graphic designer",
    "registered nurse",
    "marketing manager",
    "electrician",
]

CITIES = ["Seattle", "Chicago", "Austin", "Denver", "Portland", "Raleigh", "Phoenix", "Columbus"]


def _avatar_url(seed: str) -> str:
    """Illustrated (not real-photo) avatars — matches the app's own stance on not normalizing
    real face scraping, even in stub data."""
    return f"https://api.dicebear.com/9.x/notionists/svg?seed={seed}"


def _generate_candidates(name: str, count: int) -> list[Candidate]:
    used: set[tuple[str, str]] = set()
    candidates: list[Candidate] = []

    for i in range(count):
        occupation, city = random.choice(OCCUPATIONS), random.choice(CITIES)
        attempts = 0
        while (occupation, city) in used and attempts < 10:
            occupation, city = random.choice(OCCUPATIONS), random.choice(CITIES)
            attempts += 1
        used.add((occupation, city))

        candidate_id = f"gen_{i}_{uuid.uuid4().hex[:6]}"
        confidence = max(0.32, 0.93 - i * 0.16 - random.random() * 0.06)

        candidates.append(
            Candidate(
                id=candidate_id,
                label=f"{name}, {occupation}, {city}",
                summary=f"Works as a {occupation}, based in {city}.",
                photo_url=_avatar_url(candidate_id) if random.random() < 0.5 else None,
                confidence=round(confidence, 2),
            )
        )

    return sorted(candidates, key=lambda c: c.confidence, reverse=True)


_AMBIGUOUS_CANDIDATES: list[Candidate] = [
    Candidate(
        id="c_1",
        label="John Smith, software engineer, Seattle",
        summary="Backend engineer at Acme Corp, based in Seattle since 2019.",
        photo_url=_avatar_url("c_1"),
        confidence=0.82,
    ),
    Candidate(
        id="c_2",
        label="John Smith, attorney, Chicago",
        summary="Corporate lawyer at a Chicago firm, active in local bar association.",
        photo_url=None,
        confidence=0.71,
    ),
    Candidate(
        id="c_3",
        label="John Smith, musician, Austin",
        summary="Session guitarist and part-time producer, several regional tour credits.",
        photo_url=_avatar_url("c_3"),
        confidence=0.64,
    ),
]

_PROFILE_FIXTURE_FIELDS = ProfileFields(
    full_name="Jonathan A. Smith",
    aliases=["Jon Smith"],
    location_current="Seattle, WA",
    location_history=["Chicago, IL"],
    occupation="Software Engineer",
    employer="Acme Corp",
    education=[Education(institution="University of Washington", degree="BS, Computer Science", year=2015)],
    social_profiles=[
        SocialProfile(platform="github", url="https://github.com/jsmith", confidence=0.9),
        SocialProfile(platform="linkedin", url="https://linkedin.com/in/jonathan-a-smith", confidence=0.88),
        SocialProfile(platform="x", url="https://x.com/jsmithdev", confidence=0.62),
    ],
    photos=[_avatar_url("jonathan-a-smith")],
    summary=(
        "Jonathan Smith is a software engineer based in Seattle, currently working on backend "
        "systems at Acme Corp. Previously based in Chicago; graduated from the University of "
        "Washington in 2015."
    ),
)

_PROFILE_FIXTURE_SOURCES = [
    Source(
        url="https://acmecorp.example/team/jonathan-smith",
        title="Acme Corp — Engineering Team",
        snippet="Jonathan Smith joined Acme Corp's backend team in 2019, based in our Seattle office.",
        supports_field="employer",
    ),
    Source(
        url="https://acmecorp.example/team/jonathan-smith",
        title="Acme Corp — Engineering Team",
        snippet="Jonathan Smith joined Acme Corp's backend team in 2019, based in our Seattle office.",
        supports_field="location_current",
    ),
    Source(
        url="https://linkedin.com/in/jonathan-a-smith",
        title="Jonathan A. Smith | LinkedIn",
        snippet="BS Computer Science, University of Washington, 2015. Also goes by Jon Smith.",
        supports_field="education",
    ),
    Source(
        url="https://linkedin.com/in/jonathan-a-smith",
        title="Jonathan A. Smith | LinkedIn",
        snippet="BS Computer Science, University of Washington, 2015. Also goes by Jon Smith.",
        supports_field="aliases",
    ),
    Source(
        url="https://github.com/jsmith",
        title="jsmith (Jonathan Smith) · GitHub",
        snippet="Backend engineer. Seattle, WA. Previously Chicago, IL.",
        supports_field="location_history",
    ),
    Source(
        url="https://acmecorp.example/team/jonathan-smith",
        title="Acme Corp — Engineering Team",
        snippet="Jonathan works as a Software Engineer on the backend infrastructure team.",
        supports_field="occupation",
    ),
    Source(
        url="https://github.com/jsmith",
        title="jsmith (Jonathan Smith) · GitHub",
        snippet="Personal site links to LinkedIn and X profiles.",
        supports_field="social_profiles",
    ),
]


@dataclass
class _Store:
    """In-memory only — matches the stub's own scope. Swap for the real `search`/`profile`
    SQLite tables from docs/DATA_MODEL.md when the real pipeline lands; nothing outside this
    module reaches into these dicts directly."""

    searches: dict[str, list[Candidate]] = field(default_factory=dict)
    profiles: dict[str, ProfileResponse] = field(default_factory=dict)


_store = _Store()


async def run_search(name: str, trimmed_name: str) -> SearchResponse:
    await asyncio.sleep(SEARCH_DELAY_S)

    if name == DEV_TRIGGERS["error"]:
        raise HTTPException(
            status_code=502,
            detail={"error": "upstream_error", "message": "search API or LLM call failed"},
        )

    if name == DEV_TRIGGERS["empty"]:
        return SearchResponse(search_id=f"s_{uuid.uuid4().hex[:8]}", candidates=[], auto_selected=False)

    if name == DEV_TRIGGERS["ambiguous"]:
        search_id = f"s_{uuid.uuid4().hex[:8]}"
        _store.searches[search_id] = _AMBIGUOUS_CANDIDATES
        return SearchResponse(search_id=search_id, candidates=_AMBIGUOUS_CANDIDATES, auto_selected=False)

    # A first-name-only search collides with far more real people than a full name does — weight
    # the odds of an ambiguous result accordingly, same logic an OSINT tool actually needs.
    word_count = len(trimmed_name.split())
    ambiguous_chance = 0.6 if word_count <= 1 else 0.15
    is_ambiguous = random.random() < ambiguous_chance

    search_id = f"s_{uuid.uuid4().hex[:8]}"
    if is_ambiguous:
        candidates = _generate_candidates(trimmed_name, random.randint(2, 4))
        _store.searches[search_id] = candidates
        return SearchResponse(search_id=search_id, candidates=candidates, auto_selected=False)

    single = _generate_candidates(trimmed_name, 1)
    _store.searches[search_id] = single
    return SearchResponse(search_id=search_id, candidates=single, auto_selected=True)


async def run_select(search_id: str, candidate_id: str) -> ProfileResponse:
    candidates = _store.searches.get(search_id)
    if candidates is None:
        raise HTTPException(
            status_code=404, detail={"error": "not_found", "message": "search_id does not exist"}
        )
    if not any(c.id == candidate_id for c in candidates):
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": "candidate_id does not exist for this search"},
        )

    await asyncio.sleep(SELECT_DELAY_S)

    profile_id = f"p_{uuid.uuid4().hex[:8]}"
    profile = ProfileResponse(
        profile_id=profile_id, fields=_PROFILE_FIXTURE_FIELDS, sources=_PROFILE_FIXTURE_SOURCES
    )
    _store.profiles[profile_id] = profile
    return profile


def get_profile(profile_id: str) -> ProfileResponse | None:
    return _store.profiles.get(profile_id)
