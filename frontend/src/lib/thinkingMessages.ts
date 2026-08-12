/** Rotating status lines the UI cycles through while a request is in flight. Purely cosmetic —
 * the backend doesn't stream real progress, so these just narrate the pipeline in docs/LLM_PIPELINE.md. */
export const THINKING_MESSAGES = {
  search: [
    "Searching public sources…",
    "Scanning search-indexed social profiles…",
    "Cross-referencing results…",
    "Clustering distinct people…",
  ],
  profile: [
    "Reviewing the chosen candidate…",
    "Fetching public pages…",
    "Extracting sourced facts…",
    "Verifying every citation…",
  ],
};
