import type { ApiError } from "./types";

/** Curated, user-safe copy per error code — never the raw `message` from the API. That field is
 * a debugging aid for developers (e.g. "search_id does not exist", "search API or LLM call
 * failed") and can name internal identifiers or system architecture; it belongs in the console,
 * not the UI. */
const SAFE_MESSAGES: Record<ApiError["error"], string> = {
  not_found: "That search has expired — please start a new one.",
  validation_error: "Please check your search and try again.",
  upstream_error: "Something went wrong while searching. Please try again in a moment.",
  rate_limited: "Too many searches right now — please wait a moment and try again.",
};

const FALLBACK = "Something went wrong. Please try again.";

/** Logs the real error for developers, returns only safe copy for the UI. */
export function toSafeMessage(err: unknown): string {
  console.error("[who-is] request failed:", err);

  if (err && typeof err === "object" && "error" in err) {
    const code = (err as ApiError).error;
    return SAFE_MESSAGES[code] ?? FALLBACK;
  }
  return FALLBACK;
}
