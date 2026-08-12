import type { Candidate } from "../lib/types";
import { CandidateCard } from "./CandidateCard";

interface CandidatePickerProps {
  candidates: Candidate[];
  onSelect: (candidateId: string) => void;
}

export function CandidatePicker({ candidates, onSelect }: CandidatePickerProps) {
  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-col gap-1">
        <h2 className="font-display text-3xl text-ink">A few people go by that name.</h2>
        <p className="text-sm text-ink-soft">
          Pick the one you mean — we'll pull together everything public we can find on them.
        </p>
      </div>
      <ul className="flex flex-col gap-3">
        {candidates.map((candidate, index) => (
          <li key={candidate.id}>
            <CandidateCard candidate={candidate} index={index} onSelect={() => onSelect(candidate.id)} />
          </li>
        ))}
      </ul>
    </div>
  );
}
