# SCRAPING_SOURCES

## Search provider stack (free-tier first)

Priority order, checked in this sequence at request time:

1. **SearXNG — self-hosted metasearch, primary.** Runs as a `searxng` container in the local Docker Compose stack (see [ARCHITECTURE.md](./ARCHITECTURE.md#local-development-docker)). Free, no API key, no daily query cap — it fans a query out to dozens of upstream engines and merges results. No per-query cost means the POC isn't rate-limited by a vendor while iterating.
2. **Tavily — free-tier fallback.** 1,000 credits/month, recurring, no credit card. Used when SearXNG is unreachable (not running, e.g. a quick cloud demo) or returns too few results. Purpose-built for feeding LLM pipelines — cleaner snippets than a raw SERP.
3. ~~Google Custom Search JSON API~~ — **dropped.** It's the API the original design assumed, but Google closed it to new customers in 2025; existing customers keep their 100/day free quota only until it shuts down entirely on 2027-01-01. Not usable for a fresh signup, so it's not the primary here.
4. ~~Brave Search API~~ — considered, ruled out. Brave killed its zero-cost tier in February; new signups now get a one-time $5 credit (~1,000 queries) before metered billing kicks in. Not a sustainable free option.
5. ~~DuckDuckGo (scraped HTML results)~~ — ruled out. DuckDuckGo's ToS prohibits scraping, and it actively throttles/CAPTCHAs automated traffic — both conflict with this project's own "no direct scraping of a provider that forbids it" rule (see [CONCEPT.md](./CONCEPT.md#privacy--legal--dont-skip-this)). The official Instant Answer API is free and key-less but only returns boxed answers, not ranked web results — not useful here.

Query built from `name` + whatever filters were given (country, occupation, aliases appended as extra terms). Returns title/snippet/link per result — this is the raw input to the clustering LLM call.

## Deep dive — scoped search + direct page fetch

Runs server-side (FastAPI), so no CORS constraint — this is the reason the backend exists instead of a pure client app.

1. **More scoped queries** through the same provider stack above, now including the chosen candidate's disambiguators (employer, city, etc. — from `candidate.label`/`summary`), plus the per-platform social queries below.
2. **Direct page fetch** on the resulting URLs: `httpx` for the request, `BeautifulSoup` to strip to readable text. No JS execution — pages that need it just yield thinner content for the POC.

**Rules**
- Respect `robots.txt` — check before fetching, skip disallowed paths.
- Set a real `User-Agent`, identify the tool, don't spoof a browser.
- Rate-limit outbound fetches (e.g. 1 req/sec/domain) — don't hammer a site because one person's profile has 20 hits on it.
- Timeout + skip on failure — one dead link shouldn't fail the whole profile.

## Social media discovery (Instagram, Facebook, X, LinkedIn, TikTok, YouTube)

Same non-negotiable as everywhere else in this doc: **no authenticated or session-based scraping.** That rules out logging in, unofficial private-endpoint libraries (instaloader, snscrape's authenticated paths), and headless-browser session hijacking — all straightforward ToS violations on every platform above. What's in scope is narrower and entirely public:

1. **Discovery via search, not platform scraping.** Broad/deep-dive queries add `site:` operators for the target platforms — e.g. `"<name>" (site:instagram.com OR site:facebook.com OR site:x.com OR site:twitter.com OR site:linkedin.com OR site:tiktok.com OR site:youtube.com)` — run through the same SearXNG/Tavily stack above. This surfaces only pages the platform already lets search engines index; no new integration, no platform-specific key.
2. **Each hit is just another search result** (title/snippet/url) feeding the same clustering LLM call as any other source — no special-casing needed there.
3. **Best-effort meta-tag enrich during deep dive.** For a candidate's social URLs, `httpx`-fetch the page and read only the public `<meta property="og:*">` / `<title>` tags — the same link-preview metadata every platform serves to Slack/iMessage/Twitter-card unfurlers, no login required. If the platform bot-blocks the request instead (redirect to a login wall, CAPTCHA, non-200), skip it and fall back to the search snippet alone. Never retry with a spoofed browser or a session cookie — that's the line into scraping this doc explicitly rules out.
4. Feed the resulting platform name into `social_profiles[].platform` (`instagram` / `facebook` / `x` / `linkedin` / `tiktok` / `youtube` / `github` / `other`) — already supported by the existing schema in [DATA_MODEL.md](./DATA_MODEL.md), no change needed there.
5. Same per-domain rate limit and robots.txt rules above apply — a candidate with five hits on one platform still gets one request per second to that domain, not five at once.

## Sources still explicitly out of scope

| Source | Why deferred |
|---|---|
| Anything behind a login wall (private profiles, follower/following graphs, DMs, story content) | Requires authentication — out of scope by the rule above, not just deferred |
| LinkedIn's own search/People-You-May-Know style endpoints | Same as above — aggressive bot detection, ToS explicitly forbids it, needs its own legal review before touching |
| Paywalled/registration sites | Low value per unit of effort for a POC |

These become opt-in modules later, each with its own ToS/legal check — not bundled into the default pipeline. See [CONCEPT.md](./CONCEPT.md) phases.

## Phase 2 (only when plain fetch stops being enough)

- Playwright for JS-rendered / bot-guarded pages — heavier, slower, don't reach for it until plain `httpx` demonstrably fails on target sites.
- A paid search API (once free-tier volume is the actual bottleneck) — Tavily's paid tier or similar, not Google CSE (closed to new customers).
- Per-source adapters for LinkedIn/social beyond meta-tag enrich, gated behind explicit user opt-in and their own ToS sign-off.
