"""Covers the stub's non-trivial logic: trigger words, randomized-outcome bounds, the
search -> select -> get-profile round trip, and the documented error shapes."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ambiguous_trigger_returns_three_candidates() -> None:
    res = client.post("/api/search", json={"name": "John Smith"})
    assert res.status_code == 200
    body = res.json()
    assert body["auto_selected"] is False
    assert len(body["candidates"]) == 3


def test_empty_trigger_returns_no_candidates() -> None:
    res = client.post("/api/search", json={"name": "Test Empty"})
    assert res.status_code == 200
    body = res.json()
    assert body["candidates"] == []
    assert body["auto_selected"] is False


def test_error_trigger_returns_upstream_error() -> None:
    res = client.post("/api/search", json={"name": "Test Error"})
    assert res.status_code == 502
    assert res.json() == {"error": "upstream_error", "message": "search API or LLM call failed"}


def test_missing_name_is_a_validation_error() -> None:
    res = client.post("/api/search", json={})
    assert res.status_code == 422
    body = res.json()
    assert body["error"] == "validation_error"
    assert "name" in body["message"]


def test_generated_candidates_stay_in_bounds() -> None:
    # Run enough searches that both branches of the randomized outcome get exercised at least once.
    seen_counts = set()
    for _ in range(40):
        res = client.post("/api/search", json={"name": "Riley Chen"})
        body = res.json()
        seen_counts.add(len(body["candidates"]))
        for candidate in body["candidates"]:
            assert 0.0 <= candidate["confidence"] <= 1.0
            assert candidate["label"].startswith("Riley Chen,")
    assert seen_counts.issubset({1, 2, 3, 4})


def test_select_then_get_profile_round_trip() -> None:
    search = client.post("/api/search", json={"name": "John Smith"}).json()
    candidate_id = search["candidates"][0]["id"]

    select_res = client.post(f"/api/search/{search['search_id']}/select", json={"candidate_id": candidate_id})
    assert select_res.status_code == 200
    profile = select_res.json()
    assert profile["fields"]["full_name"]

    get_res = client.get(f"/api/profile/{profile['profile_id']}")
    assert get_res.status_code == 200
    assert get_res.json() == profile


def test_select_with_unknown_search_id_is_not_found() -> None:
    res = client.post("/api/search/does-not-exist/select", json={"candidate_id": "c_1"})
    assert res.status_code == 404
    assert res.json()["error"] == "not_found"


def test_get_unknown_profile_is_not_found() -> None:
    res = client.get("/api/profile/does-not-exist")
    assert res.status_code == 404
    assert res.json()["error"] == "not_found"
