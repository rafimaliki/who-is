# WhoIs

OSINT-style person profiler. Name in, structured profile out. POC stage — docs only, no code yet.

## Docs

Read before working on this repo: [docs/README.md](./docs/README.md) (index) → [docs/CONCEPT.md](./docs/CONCEPT.md) → [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) → rest as needed (DATA_MODEL, API_CONTRACT, LLM_PIPELINE, SCRAPING_SOURCES, FRONTEND_UX).

## Required skills — every session

Invoke both at session start, no exceptions:

- `ponytail:ponytail` (full intensity) — lazy-first implementation ladder for all code in this repo.
- `andrej-karpathy-skills:karpathy-guidelines` — avoid overcomplication, make surgical changes, surface assumptions.

## Non-negotiables (from docs/CONCEPT.md)

- Profile pages are `noindex`, always.
- Every profile field carries a source — no field renders without one.
- Search via paid APIs (Google Custom Search), never direct Google scraping.
