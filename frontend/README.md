# who-is — frontend

Astro (marketing shell, SSG) + one React island (`/app`) for the interactive search flow. See
[../docs](../docs) for the full product design; [FRONTEND_UX.md](../docs/FRONTEND_UX.md) is the
page/state reference for this directory specifically.

Talks to the [`../backend`](../backend) FastAPI service over HTTP via `personSearchService`
(`src/lib/personSearchService.ts`) — set `PUBLIC_API_BASE_URL` in `.env` if it's not running at
the default `http://localhost:8000` (see `.env.example`). The backend itself is currently a stub
— fixture data, no real search/LLM calls yet — so run both to try the app; see the backend's own
README for its dev-only test triggers.

## Commands

| Command | Action |
| --- | --- |
| `pnpm dev` | Start the dev server at `localhost:4321` (hot reload) |
| `pnpm build` | Production build to `./dist/` |
| `pnpm preview` | Preview the production build locally |

## Structure

- `src/pages/` — `/` and `/how-it-works` (static, indexed), `/app` (React island, `noindex`)
- `src/components/` — `App.tsx` owns the flow state machine; `SearchForm`, `CandidatePicker`,
  `ProfileView` are the three screens
- `src/lib/personSearchService.ts` — `PersonSearchService` interface + `HttpPersonSearchService`,
  the app's one seam for "however we find people". `src/lib/types.ts` has the shared shapes,
  mirrored from `../docs/API_CONTRACT.md` / `DATA_MODEL.md`.
- `src/lib/thinkingMessages.ts` — the rotating "thinking" lines shown while a request is in
  flight; purely cosmetic, the backend doesn't stream real progress.
- `src/styles/global.css` — Tailwind v4 + design tokens (color, font) via `@theme`
