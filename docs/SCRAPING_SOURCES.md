# SCRAPING_SOURCES

## Broad search — Google Custom Search JSON API

- Paid API (Programmable Search Engine), not scraping `google.com` directly. Avoids ToS violation and the inevitable IP ban.
- Query built from `name` + whatever filters were given (country, occupation, aliases appended as extra terms).
- Returns title/snippet/link per result — this is the raw input to the clustering LLM call.
- Quota-limited (free tier: 100 queries/day). Fine for POC, needs a paid tier or a second provider before real usage.

## Deep dive — scoped search + direct page fetch

Runs server-side (FastAPI), so no CORS constraint — this is the reason the backend exists instead of a pure client app.

1. **More scoped search queries** through the same Custom Search API, now including the chosen candidate's disambiguators (employer, city, etc. — from `candidate.label`/`summary`).
2. **Direct page fetch** on the resulting URLs: `httpx` for the request, `BeautifulSoup` to strip to readable text. No JS execution — pages that need it just yield thinner content for the POC.

**Rules**
- Respect `robots.txt` — check before fetching, skip disallowed paths.
- Set a real `User-Agent`, identify the tool, don't spoof a browser.
- Rate-limit outbound fetches (e.g. 1 req/sec/domain) — don't hammer a site because one person's profile has 20 hits on it.
- Timeout + skip on failure — one dead link shouldn't fail the whole profile.

## Sources explicitly out of scope for POC

| Source | Why deferred |
|---|---|
| LinkedIn | Aggressive bot detection, ToS explicitly forbids scraping, needs its own legal review before touching |
| Facebook/Instagram/X | Same — auth-walled, ToS-restricted, own module later |
| Paywalled/registration sites | Low value per unit of effort for a POC |

These become opt-in modules later, each with its own ToS/legal check — not bundled into the default pipeline. See [CONCEPT.md](./CONCEPT.md) phases.

## Phase 2 (only when plain fetch stops being enough)

- Playwright for JS-rendered / bot-guarded pages — heavier, slower, don't reach for it until plain `httpx` demonstrably fails on target sites.
- Per-source adapters for LinkedIn/social, gated behind explicit user opt-in and their own ToS sign-off.
