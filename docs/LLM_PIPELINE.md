# LLM_PIPELINE

Two LLM calls, both structured output via JSON schema / tool-use — never free-text parsing. Provider is free-tier-first for the POC (see [Model & params](#model--params) below) — the prompts and schemas are provider-agnostic.

## Call 1 — Clustering

**When:** right after broad search returns.
**Input:** the user's query params + the raw list of search results (title, snippet, url) from the search provider stack ([SCRAPING_SOURCES.md](./SCRAPING_SOURCES.md)) — including any social-platform hits from the `site:` queries.
**Task:** group results into N distinct people, not N search results. Two results about "John Smith the Seattle engineer" belong in one cluster even if worded differently; one result about "John Smith the Chicago lawyer" is a separate cluster.

**Output schema**
```json
{
  "candidates": [
    {
      "label": "string, short human-readable disambiguator",
      "summary": "string, 1-2 sentences",
      "photo_url": "string | null",
      "confidence": "number 0-1, how sure this is a distinct real person cluster",
      "source_urls": ["string, urls from the input that belong to this cluster"]
    }
  ]
}
```

**Prompt principles**
- Ground every cluster in `source_urls` — no cluster without at least one supporting result.
- If evidence is too thin to distinguish people, merge rather than over-split (fewer, more confident clusters beat many low-confidence ones).
- Explicitly instruct: do not invent details not present in the input snippets.

## Call 2 — Extraction

**When:** after deep dive on the chosen candidate.
**Input:** the candidate's cluster info + all deep-dive page content/snippets fetched for it.
**Task:** fill the profile field list (see [DATA_MODEL.md](./DATA_MODEL.md)) from the given text only, citing the source for each non-null field.

**Output schema**
```json
{
  "fields": {
    "full_name": "string",
    "aliases": ["string"],
    "location_current": "string | null",
    "location_history": ["string"],
    "occupation": "string | null",
    "employer": "string | null",
    "education": [{ "institution": "string", "degree": "string | null", "year": "number | null" }],
    "social_profiles": [{ "platform": "string", "url": "string", "confidence": "number" }],
    "photos": ["string"],
    "summary": "string"
  },
  "sources": [
    { "url": "string", "title": "string", "snippet": "string", "supports_field": "string" }
  ]
}
```

**Prompt principles**
- Hard rule, stated in the system prompt: **no source, no field.** If a fact can't be tied to a snippet/url in the input, leave it null — never fill from general knowledge or inference beyond the given text.
- One `sources` entry per fact used, not per field — a field can cite multiple sources.
- Low temperature (near 0) — this is extraction, not creative writing.

## Model & params

Provider stack, checked in this order (see [ARCHITECTURE.md](./ARCHITECTURE.md#why-this-split) for the "why free-tier-first" reasoning):

| Priority | Provider | Model | Free tier | Notes |
|---|---|---|---|---|
| 1 (primary) | Groq | Llama 3.3 70B / Llama 4 Scout | 30 RPM, 6K TPM, 14,400 req/day, no card | Fast inference — good fit for the POC's synchronous (blocking) API. Native JSON-mode/tool-calling for schema-forced output. |
| 2 (local fallback) | Ollama | Qwen2.5 7B/14B (tool-capable) | Unlimited, $0, runs in the `ollama` Compose profile | Zero rate limit, data never leaves the machine — the safer default whenever the input contains real people's PII and no network dependency is wanted. Weaker extraction accuracy than a frontier model; accept the tradeoff for local dev, not for quality-critical runs. |
| 3 (secondary fallback) | OpenRouter | Pick from its free pool (DeepSeek R1, Llama 3.3 70B, Qwen3, etc.) | 20 RPM, 50–1,000 req/day (higher after a one-time $10 top-up), no card | Backup when Groq is rate-limited; treat the exact free model list as unstable — it's community-curated and rotates. |

`LLM_PROVIDER` env var selects the active one (see [ARCHITECTURE.md](./ARCHITECTURE.md#secrets)); the two prompts/schemas above don't change per provider.

**Explicitly not used for the POC:** Gemini's free tier — Google's terms allow using free-tier prompts/responses to improve its products, which is a bad default when the input is PII about real people. Revisit only with a paid (training-excluded) tier.

| | |
|---|---|
| Temperature | ~0 for both calls |
| Output | tool-use / forced JSON schema, not prompt-parsed free text |
| Retry | on schema-invalid response, one retry with the validation error appended; else surface `upstream_error` |
| Later | Swap any of these for a paid frontier model (Claude, GPT) once free-tier throughput or extraction quality is the actual bottleneck — not before. |
