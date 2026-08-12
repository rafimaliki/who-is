# who-is — backend

FastAPI service implementing [`../docs/API_CONTRACT.md`](../docs/API_CONTRACT.md). Currently a
**stub**: `app/stub.py` returns fixture data with fake latency instead of running the real
search → cluster → deep dive → extract pipeline (see
[`../docs/LLM_PIPELINE.md`](../docs/LLM_PIPELINE.md) /
[`../docs/SCRAPING_SOURCES.md`](../docs/SCRAPING_SOURCES.md) for what that becomes). Swapping in
the real pipeline means replacing `run_search` / `run_select` in that one file — routes and
response shapes stay identical.

## Setup

```sh
python -m venv .venv
source .venv/Scripts/activate   # .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt   # includes requirements.txt + test deps
```

## Run

```sh
uvicorn app.main:app --reload --port 8000
```

CORS is open to the Astro dev server's origin (`localhost:4321`) only — see `app/main.py`.

## Test

```sh
pytest
```

## Dev-only test triggers

`app/stub.py` reads the search `name` field for magic values so every flow state is reachable
without a real pipeline:

| Name | Result |
| --- | --- |
| anything else | randomized — see below |
| `john smith` | 3 ambiguous candidates → picker |
| `test empty` | zero candidates → empty state |
| `test error` | simulated `502 upstream_error` |

Any other name gets a randomized outcome instead of a fixed one: a one-word ("first name only")
search skews ~60% toward multiple candidates, a full name ~15% — same logic a real disambiguation
step needs, per [`../docs/CONCEPT.md`](../docs/CONCEPT.md#why-its-hard).

## Structure

- `app/main.py` — FastAPI app, CORS, and the exception handlers that shape errors into
  `{error, message}` per the API contract instead of FastAPI's default `{"detail": ...}`
- `app/routes.py` — the three endpoints; translates HTTP <-> `stub.py` only
- `app/models.py` — Pydantic request/response models mirroring the API contract
- `app/stub.py` — the stub pipeline: fixture data, randomized-outcome logic, in-memory store
- `tests/test_stub_flow.py` — covers trigger words, the randomized-outcome bounds, the
  search → select → get-profile round trip, and the documented error shapes
