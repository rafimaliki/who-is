# FRONTEND_UX

## Pages

| Route | Rendering | Indexed? |
|---|---|---|
| `/` | Astro SSG | yes — landing, explains the product |
| `/how-it-works` | Astro SSG | yes — SEO content, also builds trust re: sourcing |
| `/app` | Astro page hosting one React island | **no** — `<meta name="robots" content="noindex">` |

Only `/app` is interactive. Everything else is static HTML, no client JS shipped.

## App island — states

Single React island on `/app`, driving three UI states off one `POST /api/search` + `POST /api/search/{id}/select` round trip:

1. **Search form** — name (required) + optional filters (country, age range, occupation, aliases). Submit → `POST /api/search`.
2. **Candidate picker** — shown only if `auto_selected: false` and `candidates.length > 1`. Cards: photo, label, summary, confidence. Pick one → `POST /api/search/{id}/select`.
   - If `auto_selected: true` (N==1), skip straight to step 3 — call `/select` immediately with the single candidate's id.
3. **Profile view** — renders `fields` from [DATA_MODEL.md](./DATA_MODEL.md), each populated field showing its `sources` inline (expandable citation, not just a footnote number nobody clicks).

## Loading / empty / error

| Case | UI |
|---|---|
| Search in flight | skeleton/spinner on submit button, form stays visible |
| Deep dive in flight | progress state on picker/profile transition — this step is the slow one, say so ("checking sources...") rather than a bare spinner |
| Zero candidates | explicit empty state: "no public results for this name + filters" — not a blank screen |
| Upstream error (502/429) | inline retry, plain-language message, no raw error JSON shown to the user |

## Components

Minimal, no component library needed for 3 screens:

- `SearchForm`
- `CandidateCard` (+ list wrapper)
- `ProfileField` (label, value, expandable source citations)
- `ProfileView` (composes `ProfileField`s from the `fields` map)

## SEO (static pages only)

- Per-page `<title>` / meta description on every Astro SSG page.
- `sitemap.xml` via Astro's sitemap integration — auto-excludes `noindex` routes.
- OG/Twitter card tags on landing + how-it-works for shareability.
- `/app` explicitly excluded from sitemap and marked `noindex` — never let a generated profile page get crawled. This is a privacy requirement, not just an SEO nicety — see [CONCEPT.md](./CONCEPT.md#privacy--legal--dont-skip-this).
