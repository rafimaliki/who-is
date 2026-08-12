import { useState, type ReactNode } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ChevronDown } from "lucide-react";
import type { Source } from "../lib/types";

interface ProfileFieldProps {
  label: string;
  sources: Source[];
  children: ReactNode;
}

/** A single profile fact with its expandable citations — the "not just a footnote number" bit. */
export function ProfileField({ label, sources, children }: ProfileFieldProps) {
  const [open, setOpen] = useState(false);
  const hasSources = sources.length > 0;

  return (
    <div className="border-[1.5px] border-border bg-paper p-4 shadow-flat-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="text-xs font-semibold tracking-wide text-ink-faint uppercase">{label}</h3>
          <div className="mt-1 text-sm text-ink">{children}</div>
        </div>
        {hasSources && (
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            aria-expanded={open}
            className="flex shrink-0 items-center gap-1 rounded-md border-[1.5px] border-ink bg-indigo-tint px-2.5 py-1 font-mono text-xs font-medium text-indigo-dark transition-colors hover:bg-indigo hover:text-paper"
          >
            {sources.length} source{sources.length > 1 ? "s" : ""}
            <ChevronDown
              className={`h-3.5 w-3.5 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
              aria-hidden="true"
            />
          </button>
        )}
      </div>
      <AnimatePresence initial={false}>
        {open && hasSources && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <ul className="mt-3 flex flex-col gap-2 border-t-[1.5px] border-border pt-3">
              {sources.map((s, i) => (
                <li key={`${s.url}-${i}`} className="border border-border bg-canvas px-3 py-2 text-xs">
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noreferrer"
                    className="font-medium text-indigo-dark hover:underline"
                  >
                    {s.title}
                  </a>
                  <p className="mt-0.5 text-ink-soft">{s.snippet}</p>
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
