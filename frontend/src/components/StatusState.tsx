import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Loader2, SearchX, TriangleAlert } from "lucide-react";

interface StatusStateProps {
  kind: "loading" | "empty" | "error";
  message: string | string[];
  onRetry?: () => void;
}

const ICONS = {
  loading: Loader2,
  empty: SearchX,
  error: TriangleAlert,
};

const ICON_STYLES = {
  loading: "text-indigo animate-spin",
  empty: "text-ink-faint",
  error: "text-rose",
};

/** Cycles through a list of "thinking" lines on an interval — a static message otherwise. */
function useCyclingMessage(message: string | string[], intervalMs = 850) {
  const messages = Array.isArray(message) ? message : [message];
  const [index, setIndex] = useState(0);

  useEffect(() => {
    setIndex(0);
    if (messages.length <= 1) return;
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % messages.length);
    }, intervalMs);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [Array.isArray(message) ? message.join("|") : message]);

  return messages[index]!;
}

export function StatusState({ kind, message, onRetry }: StatusStateProps) {
  const Icon = ICONS[kind];
  const current = useCyclingMessage(message);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="mt-6 flex flex-col items-center gap-3 border-[1.5px] border-ink bg-paper px-6 py-10 text-center shadow-flat"
    >
      <Icon className={`h-6 w-6 ${ICON_STYLES[kind]}`} aria-hidden="true" />
      <AnimatePresence mode="wait">
        <motion.p
          key={current}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="max-w-sm font-mono text-sm text-ink-soft"
        >
          {current}
        </motion.p>
      </AnimatePresence>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-1 border border-border px-4 py-1.5 text-sm font-medium text-ink transition-colors hover:border-ink"
        >
          Try again
        </button>
      )}
    </motion.div>
  );
}
