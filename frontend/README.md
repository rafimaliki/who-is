# who-is — frontend

Astro (marketing shell, SSG) + one React island (`/app`) for the interactive search flow. See
[../docs](../docs) for the full product design; [FRONTEND_UX.md](../docs/FRONTEND_UX.md) is the
page/state reference for this directory specifically.

Currently wired to `src/lib/mockApi.ts` — stubbed responses, no backend yet. Swapping to the real
FastAPI backend later means replacing the two functions in that file only.

## Commands

| Command | Action |
| --- | --- |
| `pnpm dev` | Start the dev server at `localhost:4321` (hot reload) |
| `pnpm build` | Production build to `./dist/` |
| `pnpm preview` | Preview the production build locally |

## Dev-only test triggers

`mockApi.ts` reads the search `name` field for magic values so every flow state is reachable
without a backend:

| Name | Result |
| --- | --- |
| anything else | single auto-selected candidate → profile |
| `john smith` | 3 ambiguous candidates → picker |
| `test empty` | zero candidates → empty state |
| `test error` | simulated upstream error |

## Structure

- `src/pages/` — `/` and `/how-it-works` (static, indexed), `/app` (React island, `noindex`)
- `src/components/` — `App.tsx` owns the flow state machine; `SearchForm`, `CandidatePicker`,
  `ProfileView` are the three screens
- `src/lib/types.ts` — shapes mirrored from `../docs/API_CONTRACT.md` / `DATA_MODEL.md`
- `src/styles/global.css` — Tailwind v4 + design tokens (color, font) via `@theme`
