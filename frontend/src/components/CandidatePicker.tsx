import type { Candidate } from "../lib/types";

// PLACEHOLDER — functional but minimally styled. Replaced by the CandidatePicker feature branch
// with photo/confidence cards and stagger-in motion. Keep the props contract stable.

interface CandidatePickerProps {
  candidates: Candidate[];
  onSelect: (candidateId: string) => void;
}

export function CandidatePicker({ candidates, onSelect }: CandidatePickerProps) {
  return (
    <div className="flex flex-col gap-3">
      <h2 className="font-display text-2xl">Which one?</h2>
      {candidates.map((c) => (
        <button
          key={c.id}
          type="button"
          onClick={() => onSelect(c.id)}
          className="rounded-xl border border-border bg-paper px-4 py-3 text-left"
        >
          <p className="font-medium">{c.label}</p>
          <p className="text-sm text-ink-soft">{c.summary}</p>
        </button>
      ))}
    </div>
  );
}
