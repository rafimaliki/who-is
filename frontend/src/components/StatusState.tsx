import { motion } from "motion/react";
import { Loader2, SearchX, TriangleAlert } from "lucide-react";

interface StatusStateProps {
  kind: "loading" | "empty" | "error";
  message: string;
  onRetry?: () => void;
}

const ICONS = {
  loading: Loader2,
  empty: SearchX,
  error: TriangleAlert,
};

const ICON_STYLES = {
  loading: "text-violet animate-spin",
  empty: "text-ink-faint",
  error: "text-coral",
};

export function StatusState({ kind, message, onRetry }: StatusStateProps) {
  const Icon = ICONS[kind];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="mt-6 flex flex-col items-center gap-3 rounded-2xl border border-border bg-paper px-6 py-10 text-center shadow-card"
    >
      <Icon className={`h-7 w-7 ${ICON_STYLES[kind]}`} aria-hidden="true" />
      <p className="max-w-sm text-sm text-ink-soft">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-1 rounded-full border border-border px-4 py-1.5 text-sm font-medium text-ink transition-colors hover:border-coral hover:text-coral"
        >
          Try again
        </button>
      )}
    </motion.div>
  );
}
