import { useCallback, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { personSearchService } from "../lib/personSearchService";
import { THINKING_MESSAGES } from "../lib/thinkingMessages";
import type { ApiError, Candidate, ProfileResponse, SearchRequest } from "../lib/types";
import { SearchForm } from "./SearchForm";
import { CandidatePicker } from "./CandidatePicker";
import { ProfileView } from "./ProfileView";
import { StatusState } from "./StatusState";

type FlowState =
  | { step: "form" }
  | { step: "searching" }
  | { step: "picker"; searchId: string; candidates: Candidate[] }
  | { step: "loading-profile" }
  | { step: "profile"; profile: ProfileResponse }
  | { step: "empty" }
  | { step: "error"; message: string };

// The "searching" step covers two different waits depending on outcome: while we don't yet know
// whether there's one match or several, and then — only when there's exactly one, so it resolves
// silently with no picker click to hang a second box on — the profile build too. This just swaps
// which thinking-message list the (still-visible) search button cycles through.
type SearchPhase = "search" | "profile";

function errorMessage(err: unknown): string {
  return err && typeof err === "object" && "message" in err ? String((err as ApiError).message) : "Something went wrong.";
}

export default function App() {
  const [state, setState] = useState<FlowState>({ step: "form" });
  const [searchPhase, setSearchPhase] = useState<SearchPhase>("search");

  const runSearch = useCallback(async (req: SearchRequest) => {
    setSearchPhase("search");
    setState({ step: "searching" });
    try {
      const res = await personSearchService.search(req);
      if (res.candidates.length === 0) {
        setState({ step: "empty" });
        return;
      }
      if (res.auto_selected) {
        // Stay on "searching" — the button keeps thinking, just about the profile now — instead
        // of a second standalone box for a candidate the user never explicitly picked.
        setSearchPhase("profile");
        const profile = await personSearchService.select(res.search_id, res.candidates[0].id);
        setState({ step: "profile", profile });
        return;
      }
      setState({ step: "picker", searchId: res.search_id, candidates: res.candidates });
    } catch (err) {
      setState({ step: "error", message: errorMessage(err) });
    }
  }, []);

  const runSelect = useCallback(
    async (searchId: string, candidateId: string) => {
      // Here the user *did* explicitly pick a candidate off a list that's no longer on screen —
      // that deliberate action earns its own standalone "reviewing your pick" box.
      setState({ step: "loading-profile" });
      try {
        const profile = await personSearchService.select(searchId, candidateId);
        setState({ step: "profile", profile });
      } catch (err) {
        setState({ step: "error", message: errorMessage(err) });
      }
    },
    [],
  );

  const reset = useCallback(() => setState({ step: "form" }), []);

  const showForm = state.step !== "picker" && state.step !== "loading-profile" && state.step !== "profile";

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-10 sm:px-6 sm:py-16">
      {showForm && (
        <SearchForm
          onSubmit={runSearch}
          isSubmitting={state.step === "searching"}
          thinkingMessages={searchPhase === "search" ? THINKING_MESSAGES.search : THINKING_MESSAGES.profile}
        />
      )}

      <AnimatePresence mode="wait">
        {state.step !== "form" && state.step !== "searching" && (
          <motion.div
            key={state.step}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          >
            {state.step === "picker" && (
              <CandidatePicker
                candidates={state.candidates}
                onSelect={(candidateId) => runSelect(state.searchId, candidateId)}
              />
            )}
            {state.step === "loading-profile" && (
              <StatusState kind="loading" message={THINKING_MESSAGES.profile} />
            )}
            {state.step === "profile" && <ProfileView profile={state.profile} onNewSearch={reset} />}
            {state.step === "empty" && (
              <StatusState
                kind="empty"
                message="No public results for this name and filters."
                onRetry={reset}
              />
            )}
            {state.step === "error" && (
              <StatusState kind="error" message={state.message} onRetry={reset} />
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
