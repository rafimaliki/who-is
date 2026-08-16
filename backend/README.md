# who-is — backend

FastAPI service implementing [`../.docs/API_CONTRACT.md`](../.docs/API_CONTRACT.md): a real
search → cluster → deep dive → extract pipeline, per
[`../.docs/LLM_PIPELINE.md`](../.docs/LLM_PIPELINE.md) and
[SearXNG](https://docs.searxng.org/)
(self-hosted, see the repo-root `docker-compose.yml`) for search, [OpenRouter](https://openrouter.ai/)
for clustering/extraction, `httpx` + BeautifulSoup for the deep-dive page fetch.

## Setup

The easiest path is `docker compose up` from the repo root (starts SearXNG + this service +
the frontend together) — see the repo root README. To run standalone instead:

```sh
python -m venv .venv
source .venv/Scripts/activate   # .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt   # includes requirements.txt + test deps
```

Needs a running SearXNG instance (`SEARXNG_URL`, defaults to `http://localhost:8080`) and an
OpenRouter API key (`OPENROUTER_API_KEY` — get one at [openrouter.ai](https://openrouter.ai/keys)).
Copy `../.env.example` to `../.env` and fill in the key; `OPENROUTER_MODEL` defaults to
`dots-studio/dots-3-note-preview:free`.

## Run

```sh
uvicorn app.main:app --reload --port 8000
```

CORS is open to the Astro dev server's origin (`localhost:4321`) and Cloudflare quick tunnels
only — see `app/main.py`.

## Test

```sh
pytest
```

Tests mock SearXNG/OpenRouter/page-fetch — no live network calls, no API cost, no dependency on a
running SearXNG instance. Live end-to-end behavior is verified manually (real search, real LLM
calls) against the actual running stack.

## Structure

Domain modules, each `route.py` (HTTP <-> service only) / `service.py` (logic) / `types.py`
(Pydantic shapes) — the folder is the "module name", the file is the "kind", so e.g.
`app.search.route` reads the same as the `search.route` naming convention this follows, via
Python's own package system instead of dots-in-filenames (which Python can't import directly).

- `app/main.py` — FastAPI app, CORS, the exception handlers that shape every error into
  `{error, message}` per the API contract instead of FastAPI's default `{"detail": ...}`
- `app/config.py` — environment-backed settings (`SEARXNG_URL`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`)
- `app/shared/` — `types.py` (shapes genuinely used by both search and profile — `ProfileFields`,
  `Source`, etc.) and `store.py` (the in-memory search/profile store both domains read or write)
- `app/search/` — `POST /api/search` + `POST /api/search/{id}/select`. `service.py` is the
  pipeline orchestration: builds the query, calls SearXNG, calls the LLM to cluster, and — on
  select — runs the scoped deep-dive search + page fetch + extraction
- `app/profile/` — `GET /api/profile/{id}`, reading from the shared store
- `app/llm/` — OpenRouter calls (`cluster_candidates`, `extract_profile`), structured output only
  (Pydantic `response_schema`), never free-text parsing
- `app/searxng/` — thin JSON-API client for the self-hosted SearXNG instance
- `app/scraping/` — direct page fetch for the deep-dive step: robots.txt, real User-Agent,
  per-domain rate limit, skip-not-fail on error
- `tests/test_search_service.py` — `app/search/service.py`'s orchestration, error mapping, and
  the store round trip, with SearXNG/OpenRouter/page-fetch mocked
