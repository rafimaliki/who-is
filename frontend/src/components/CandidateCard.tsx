import { useEffect, useState } from "react";
import { motion, useMotionValue, animate } from "motion/react";
import { User } from "lucide-react";
import type { Candidate } from "../lib/types";

interface CandidateCardProps {
  candidate: Candidate;
  index: number;
  onSelect: () => void;
}

// Rotates per card so a run of results doesn't read as one flat color block.
const AVATAR_PALETTE = [
  { bg: "bg-indigo-tint", text: "text-indigo-dark" },
  { bg: "bg-rose-tint", text: "text-rose-dark" },
  { bg: "bg-amber-tint", text: "text-amber-dark" },
];

function initials(label: string): string {
  const words = label.split(",")[0]!.trim().split(/\s+/).filter(Boolean);
  const chars = [words[0]?.[0], words[words.length - 1]?.[0]].filter(Boolean);
  return chars.join("").toUpperCase();
}

// Higher confidence reads as settled (green), lower reads as tentative (rose) — same
// three-tier logic a human would apply eyeballing a match score.
function confidenceStyle(confidence: number) {
  if (confidence >= 0.75) {
    return { label: "Strong match", bar: "bg-green", track: "bg-green-tint", text: "text-green-dark" };
  }
  if (confidence >= 0.5) {
    return { label: "Possible match", bar: "bg-amber", track: "bg-amber-tint", text: "text-amber-dark" };
  }
  return { label: "Weak match", bar: "bg-rose", track: "bg-rose-tint", text: "text-rose-dark" };
}

/** Counts up from 0 to the target percentage once, on mount — a small "computing this live" beat. */
function useCountUp(target: number, delayS: number) {
  const value = useMotionValue(0);
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const unsub = value.on("change", (v) => setDisplay(Math.round(v)));
    const controls = animate(value, target, { duration: 0.7, delay: delayS, ease: [0.16, 1, 0.3, 1] });
    return () => {
      unsub();
      controls.stop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target, delayS]);

  return display;
}

export function CandidateCard({ candidate, index, onSelect }: CandidateCardProps) {
  const [imgFailed, setImgFailed] = useState(false);
  const palette = AVATAR_PALETTE[index % AVATAR_PALETTE.length]!;
  const confidence = confidenceStyle(candidate.confidence);
  const targetPct = Math.round(candidate.confidence * 100);
  const delayS = 0.35 + index * 0.08;
  const pct = useCountUp(targetPct, delayS);
  const initialsText = initials(candidate.label);

  return (
    <motion.button
      type="button"
      onClick={onSelect}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ x: -2, y: -2 }}
      whileTap={{ x: 0, y: 0 }}
      className="flex w-full items-start gap-4 border-[1.5px] border-ink bg-paper p-4 text-left shadow-flat transition-shadow hover:shadow-[4px_4px_0_0_var(--color-ink)] active:shadow-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo focus-visible:ring-offset-2 focus-visible:ring-offset-canvas sm:p-5"
    >
      {candidate.photo_url && !imgFailed ? (
        <img
          src={candidate.photo_url}
          alt=""
          onError={() => setImgFailed(true)}
          className="h-12 w-12 shrink-0 rounded-md border-[1.5px] border-ink object-cover sm:h-14 sm:w-14"
        />
      ) : (
        <div
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-md border-[1.5px] border-ink font-display text-base font-bold sm:h-14 sm:w-14 sm:text-lg ${palette.bg} ${palette.text}`}
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
          <div className={`h-1.5 w-full max-w-24 overflow-hidden rounded-sm ${confidence.track}`}>
            <motion.div
              className={`h-full rounded-sm ${confidence.bar}`}
              initial={{ width: 0 }}
              animate={{ width: `${targetPct}%` }}
              transition={{ duration: 0.7, delay: delayS, ease: [0.16, 1, 0.3, 1] }}
            />
          </div>
          <span className={`font-mono text-xs font-medium whitespace-nowrap ${confidence.text}`}>
            {pct}% · {confidence.label}
          </span>
        </div>
      </div>
    </motion.button>
  );
}
