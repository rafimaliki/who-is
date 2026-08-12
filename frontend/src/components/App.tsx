import { useCallback, useState } from "react";
import { searchPerson, selectCandidate } from "../lib/mockApi";
import type { Candidate, ProfileResponse, SearchRequest } from "../lib/types";
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

export default function App() {
  const [state, setState] = useState<FlowState>({ step: "form" });

  const runSearch = useCallback(async (req: SearchRequest) => {
    setState({ step: "searching" });
    try {
      const res = await searchPerson(req);
      if (res.candidates.length === 0) {
        setState({ step: "empty" });
        return;
      }
      if (res.auto_selected) {
        setState({ step: "loading-profile" });
        const profile = await selectCandidate(res.search_id, res.candidates[0].id);
        setState({ step: "profile", profile });
        return;
      }
      setState({ step: "picker", searchId: res.search_id, candidates: res.candidates });
    } catch (err) {
      const message = err && typeof err === "object" && "message" in err ? String((err as { message: unknown }).message) : "Something went wrong.";
      setState({ step: "error", message });
    }
  }, []);

  const runSelect = useCallback(
    async (searchId: string, candidateId: string) => {
      setState({ step: "loading-profile" });
      try {
        const profile = await selectCandidate(searchId, candidateId);
        setState({ step: "profile", profile });
      } catch (err) {
        const message = err && typeof err === "object" && "message" in err ? String((err as { message: unknown }).message) : "Something went wrong.";
        setState({ step: "error", message });
      }
    },
    [],
  );

  const reset = useCallback(() => setState({ step: "form" }), []);

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col px-4 py-10 sm:px-6 sm:py-16">
      {state.step === "form" && <SearchForm onSubmit={runSearch} isSubmitting={false} />}
      {state.step === "searching" && (
        <>
          <SearchForm onSubmit={runSearch} isSubmitting />
          <StatusState kind="loading" message="Searching public sources…" />
        </>
      )}
      {state.step === "picker" && (
        <CandidatePicker
          candidates={state.candidates}
          onSelect={(candidateId) => runSelect(state.searchId, candidateId)}
        />
      )}
      {state.step === "loading-profile" && (
        <StatusState kind="loading" message="Checking sources and building the profile…" />
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
    </div>
  );
}
