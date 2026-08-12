import { useState } from "react";
import { motion } from "motion/react";
import { User } from "lucide-react";
import type { Candidate } from "../lib/types";

interface CandidateCardProps {
  candidate: Candidate;
  index: number;
  onSelect: () => void;
}

// Rotates per card so a run of results doesn't read as one flat color block.
const AVATAR_PALETTE = [
  { bg: "bg-coral-light", text: "text-coral-dark" },
  { bg: "bg-violet-light", text: "text-violet-dark" },
  { bg: "bg-mint-light", text: "text-mint" },
];

function initials(label: string): string {
  const words = label.split(",")[0]!.trim().split(/\s+/).filter(Boolean);
  const chars = [words[0]?.[0], words[words.length - 1]?.[0]].filter(Boolean);
  return chars.join("").toUpperCase();
}

// Higher confidence reads as settled (mint), lower reads as tentative (coral) — same
// three-tier logic a human would apply eyeballing a match score.
function confidenceStyle(confidence: number) {
  if (confidence >= 0.75) {
    return { label: "Strong match", bar: "bg-mint", track: "bg-mint-light", text: "text-mint" };
  }
  if (confidence >= 0.5) {
    return { label: "Possible match", bar: "bg-violet", track: "bg-violet-light", text: "text-violet-dark" };
  }
  return { label: "Weak match", bar: "bg-coral", track: "bg-coral-light", text: "text-coral-dark" };
}

export function CandidateCard({ candidate, index, onSelect }: CandidateCardProps) {
  const [imgFailed, setImgFailed] = useState(false);
  const palette = AVATAR_PALETTE[index % AVATAR_PALETTE.length]!;
  const confidence = confidenceStyle(candidate.confidence);
  const pct = Math.round(candidate.confidence * 100);
  const initialsText = initials(candidate.label);

  return (
    <motion.button
      type="button"
      onClick={onSelect}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: index * 0.08, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.99 }}
      className="flex w-full items-start gap-4 rounded-2xl border border-border bg-paper p-4 text-left shadow-card transition-[border-color,box-shadow] hover:border-coral hover:shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-coral focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:p-5"
    >
      {candidate.photo_url && !imgFailed ? (
        <img
          src={candidate.photo_url}
          alt=""
          onError={() => setImgFailed(true)}
          className="h-12 w-12 shrink-0 rounded-full object-cover sm:h-14 sm:w-14"
        />
      ) : (
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full font-display text-base font-medium sm:h-14 sm:w-14 sm:text-lg ${palette.bg} ${palette.text}`}
        >
          {initialsText ? initialsText : <User className="h-5 w-5" aria-hidden="true" />}
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col gap-2 pt-0.5">
        <div>
          <p className="font-medium text-ink">{candidate.label}</p>
          <p className="mt-0.5 text-sm text-ink-soft">{candidate.summary}</p>
        </div>

        <div className="flex items-center gap-2">
          <div className={`h-1.5 w-full max-w-24 overflow-hidden rounded-full ${confidence.track}`}>
            <div className={`h-full rounded-full ${confidence.bar}`} style={{ width: `${pct}%` }} />
          </div>
          <span className={`text-xs font-medium whitespace-nowrap ${confidence.text}`}>
            {pct}% · {confidence.label}
          </span>
        </div>
      </div>
    </motion.button>
  );
}
