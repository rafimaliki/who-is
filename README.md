# who-is

OSINT-style person profiler. Type a name, get a structured, source-cited profile back. See
[`.docs/`](./.docs) for the full product design — start with
[`.docs/CONCEPT.md`](./.docs/CONCEPT.md).

## Quick start

```sh
cp .env.example .env   # then fill in OPENROUTER_API_KEY (get one at openrouter.ai/keys)
docker compose up
```

- Frontend: http://localhost:4321
- Backend: http://localhost:8000
- SearXNG (search provider, self-hosted): http://localhost:8080

All three run with hot reload — edit `frontend/` or `backend/` source and it picks up the change.

## Structure

| Directory | What |
| --- | --- |
| [`.docs/`](./.docs) | Product design docs — read these first |
| [`frontend/`](./frontend) | Astro + one React island, talks to the backend over HTTP |
| [`backend/`](./backend) | FastAPI: search → cluster → deep dive → extract pipeline (SearXNG + Gemini) |
| [`searxng/`](./searxng) | Config override for the self-hosted SearXNG container |

Each service's own README has its specific setup/run/test instructions if you'd rather run it
standalone instead of through `docker compose`.
