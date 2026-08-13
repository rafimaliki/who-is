"""Unit tests for app/search/service.py's orchestration — query building, the store round trip,
and error mapping — with SearXNG/Gemini/page-fetch mocked out. Those are real network calls to a
self-hosted instance and a paid API; a test suite shouldn't depend on either being reachable or
cost money to run. Live end-to-end behavior is verified manually against a real SearXNG + Gemini
key (see backend/README.md)."""

import pytest
from fastapi import HTTPException

from app.llm import service as llm
from app.llm.types import ClusterCandidate, ClusterOutput, ExtractFields, ExtractOutput, ExtractSource
from app.profile import service as profile_service
from app.scraping import service as scraping
from app.search import service as search_service
from app.searxng import service as searxng
from app.searxng.types import SearxResult


def _result(url: str, title: str = "Title", content: str = "Snippet") -> SearxResult:
    return SearxResult(title=title, url=url, content=content)


async def test_search_returns_candidates_from_clustered_results(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_search(*_a: object, **_k: object) -> list[SearxResult]:
        return [_result("https://a.example"), _result("https://b.example")]

    async def fake_cluster(*_a: object, **_k: object) -> ClusterOutput:
        return ClusterOutput(
            candidates=[
                ClusterCandidate(label="Jane Doe, engineer", summary="...", confidence=0.8, source_urls=["https://a.example"]),
                ClusterCandidate(label="Jane Doe, teacher", summary="...", confidence=0.6, source_urls=["https://b.example"]),
            ]
        )

    monkeypatch.setattr(searxng, "search", fake_search)
    monkeypatch.setattr(llm, "cluster_candidates", fake_cluster)

    res = await search_service.run_search("Jane Doe", {"country": "US", "aliases": None})

    assert res.auto_selected is False
    assert len(res.candidates) == 2
    assert res.candidates[0].label == "Jane Doe, engineer"
    assert res.search_id.startswith("s_")


async def test_search_with_no_results_skips_the_llm_call(monkeypatch: pytest.MonkeyPatch) -> None:
    async def empty(*_a: object, **_k: object) -> list[SearxResult]:
        return []

    called = False

    async def fake_cluster(*_a: object, **_k: object) -> ClusterOutput:
        nonlocal called
        called = True
        return ClusterOutput(candidates=[])

    monkeypatch.setattr(searxng, "search", empty)
    monkeypatch.setattr(llm, "cluster_candidates", fake_cluster)

    res = await search_service.run_search("Nobody Findable", {})

    assert res.candidates == []
    assert called is False  # no point asking the LLM to cluster zero results


async def test_single_candidate_is_auto_selected(monkeypatch: pytest.MonkeyPatch) -> None:
    async def one_result(*_a: object, **_k: object) -> list[SearxResult]:
        return [_result("https://a.example")]

    async def fake_cluster(*_a: object, **_k: object) -> ClusterOutput:
        return ClusterOutput(
            candidates=[ClusterCandidate(label="Solo Person", summary="...", confidence=0.9, source_urls=["https://a.example"])]
        )

    monkeypatch.setattr(searxng, "search", one_result)
    monkeypatch.setattr(llm, "cluster_candidates", fake_cluster)

    res = await search_service.run_search("Solo Person", {})

    assert res.auto_selected is True
    assert len(res.candidates) == 1


async def test_searxng_failure_maps_to_upstream_error(monkeypatch: pytest.MonkeyPatch) -> None:
    async def boom(*_a: object, **_k: object) -> list[SearxResult]:
        raise RuntimeError("connection refused")

    monkeypatch.setattr(searxng, "search", boom)

    with pytest.raises(HTTPException) as exc_info:
        await search_service.run_search("Anyone", {})

    assert exc_info.value.status_code == 502
    assert exc_info.value.detail["error"] == "upstream_error"


async def test_gemini_rate_limit_maps_to_429(monkeypatch: pytest.MonkeyPatch) -> None:
    async def some_results(*_a: object, **_k: object) -> list[SearxResult]:
        return [_result("https://a.example")]

    async def rate_limited(*_a: object, **_k: object) -> ClusterOutput:
        raise RuntimeError("429 RESOURCE_EXHAUSTED: quota exceeded")

    monkeypatch.setattr(searxng, "search", some_results)
    monkeypatch.setattr(llm, "cluster_candidates", rate_limited)

    with pytest.raises(HTTPException) as exc_info:
        await search_service.run_search("Anyone", {})

    assert exc_info.value.status_code == 429
    assert exc_info.value.detail["error"] == "rate_limited"


async def test_select_then_get_profile_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    async def one_result(*_a: object, **_k: object) -> list[SearxResult]:
        return [_result("https://a.example")]

    async def fake_cluster(*_a: object, **_k: object) -> ClusterOutput:
        return ClusterOutput(
            candidates=[ClusterCandidate(label="Jane Doe", summary="Engineer", confidence=0.9, source_urls=["https://a.example"])]
        )

    monkeypatch.setattr(searxng, "search", one_result)
    monkeypatch.setattr(llm, "cluster_candidates", fake_cluster)

    search_res = await search_service.run_search("Jane Doe", {})
    candidate_id = search_res.candidates[0].id

    async def no_fetch(_url: str) -> str | None:
        return None  # forces the search-snippet fallback path

    async def fake_extract(*_a: object, **_k: object) -> ExtractOutput:
        return ExtractOutput(
            fields=ExtractFields(
                full_name="Jane Doe",
                aliases=[],
                location_current="Seattle, WA",
                location_history=[],
                occupation="Engineer",
                employer=None,
                education=[],
                social_profiles=[],
                photos=[],
                summary="Jane Doe is an engineer.",
            ),
            sources=[ExtractSource(url="https://a.example", title="Title", snippet="Snippet", supports_field="location_current")],
        )

    monkeypatch.setattr(scraping, "fetch_text", no_fetch)
    monkeypatch.setattr(llm, "extract_profile", fake_extract)

    profile = await search_service.run_select(search_res.search_id, candidate_id)
    assert profile.fields.full_name == "Jane Doe"

    fetched = profile_service.get_profile(profile.profile_id)
    assert fetched == profile


async def test_select_with_unknown_search_id_is_not_found() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await search_service.run_select("does-not-exist", "c_1")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["error"] == "not_found"


async def test_get_unknown_profile_is_none() -> None:
    assert profile_service.get_profile("does-not-exist") is None
