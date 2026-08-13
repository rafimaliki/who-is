# API_CONTRACT

Backend is FastAPI, JSON only. POC is synchronous — each endpoint blocks until its step finishes (no job queue yet, see [CONCEPT.md](./CONCEPT.md) phases).

## `POST /api/search`

Kicks off broad search + clustering.

**Request**
```json
{
  "name": "John Smith",
  "country": "US",
  "age_range": "30-40",
  "occupation": "software engineer",
  "aliases": ["Jon Smith"]
}
```
Only `name` is required.

**Response `200`**
```json
{
  "search_id": "s_abc123",
  "candidates": [
    {
      "id": "c_1",
      "label": "John Smith, software engineer, Seattle",
      "summary": "Backend engineer at Acme Corp, based in Seattle since 2019.",
      "photo_url": "https://...",
      "confidence": 0.82
    }
  ],
  "auto_selected": false
}
```
`auto_selected: true` means only one candidate was found — frontend skips the picker and immediately calls `/select`.

## `POST /api/search/{search_id}/select`

Runs the deep dive on the chosen candidate and extracts the profile.

**Request**
```json
{ "candidate_id": "c_1" }
```

**Response `200`**
```json
{
  "profile_id": "p_xyz789",
  "fields": {
    "full_name": "Jonathan A. Smith",
    "aliases": ["Jon Smith"],
    "location_current": "Seattle, WA",
    "location_history": ["Chicago, IL"],
    "occupation": "Software Engineer",
    "employer": "Acme Corp",
    "education": [{ "institution": "UW", "degree": "BS CS", "year": 2015 }],
    "social_profiles": [{ "platform": "github", "url": "https://github.com/jsmith", "confidence": 0.9 }],
    "photos": ["https://..."],
    "summary": "Jonathan Smith is a software engineer based in Seattle..."
  },
  "sources": [
    { "url": "https://...", "title": "...", "snippet": "...", "supports_field": "employer" }
  ]
}
```

## `GET /api/profile/{profile_id}`

Fetch a previously generated profile (page refresh / share link within the app). Same shape as the `select` response body.

## Errors

```json
{ "error": "not_found", "message": "search_id does not exist" }
```

| status | error | when |
|---|---|---|
| 404 | `not_found` | bad search/profile/candidate id |
| 422 | `validation_error` | missing `name`, bad filter shape (FastAPI default) |
| 502 | `upstream_error` | search API or LLM call failed |
| 429 | `rate_limited` | search provider quota hit |

## Not in POC scope

- Auth / API keys for callers — single-user local POC, add when it's multi-user.
- Async job status polling (`GET /api/search/{id}/status`) — add once a run takes long enough that a single blocking request is a problem.
