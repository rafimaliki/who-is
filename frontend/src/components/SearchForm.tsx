import { useId, useState, type FormEvent } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Search, SlidersHorizontal, Loader2 } from "lucide-react";
import type { SearchRequest } from "../lib/types";

interface SearchFormProps {
  onSubmit: (req: SearchRequest) => void;
  isSubmitting: boolean;
}

const FILTER_FIELDS = [
  { key: "country", label: "Country", placeholder: "e.g. United States" },
  { key: "age_range", label: "Age range", placeholder: "e.g. 30-40" },
  { key: "occupation", label: "Occupation", placeholder: "e.g. software engineer" },
  { key: "aliases", label: "Aliases", placeholder: "e.g. Jon Smith, JSmith" },
] as const;

export function SearchForm({ onSubmit, isSubmitting }: SearchFormProps) {
  const [name, setName] = useState("");
  const [filters, setFilters] = useState({ country: "", age_range: "", occupation: "", aliases: "" });
  const [showFilters, setShowFilters] = useState(false);
  const filtersId = useId();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmedName = name.trim();
    if (!trimmedName) return;

    const req: SearchRequest = { name: trimmedName };
    if (filters.country.trim()) req.country = filters.country.trim();
    if (filters.age_range.trim()) req.age_range = filters.age_range.trim();
    if (filters.occupation.trim()) req.occupation = filters.occupation.trim();
    const aliases = filters.aliases
      .split(",")
      .map((a) => a.trim())
      .filter(Boolean);
    if (aliases.length > 0) req.aliases = aliases;

    onSubmit(req);
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="flex flex-col gap-6 rounded-2xl border border-border bg-paper p-6 shadow-card sm:p-8"
    >
      <div className="flex flex-col gap-2">
        <h1 className="font-display text-4xl leading-tight text-ink sm:text-5xl">
          Who is<span className="text-coral">?</span>
        </h1>
        <p className="text-sm text-ink-soft sm:text-base">
          Give us a name. We'll dig up what's public and hand you a sourced profile.
        </p>
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="name" className="text-sm font-medium text-ink">
          Full name
        </label>
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-ink-faint"
            aria-hidden="true"
          />
          <input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Jane Doe"
            disabled={isSubmitting}
            required
            className="w-full rounded-xl border border-border bg-paper py-3.5 pl-11 pr-4 text-base text-ink placeholder:text-ink-faint transition-colors focus:border-coral focus:outline-none focus:ring-2 focus:ring-coral-light disabled:opacity-60"
          />
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <button
          type="button"
          onClick={() => setShowFilters((v) => !v)}
          aria-expanded={showFilters}
          aria-controls={filtersId}
          className="flex w-fit items-center gap-1.5 text-sm font-medium text-ink-soft transition-colors hover:text-violet"
        >
          <SlidersHorizontal className="h-3.5 w-3.5" aria-hidden="true" />
          {showFilters ? "Hide filters" : "Add filters"}
        </button>

        <AnimatePresence initial={false}>
          {showFilters && (
            <motion.div
              id={filtersId}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
              className="overflow-hidden"
            >
              <div className="grid grid-cols-1 gap-3 pt-1 sm:grid-cols-2">
                {FILTER_FIELDS.map(({ key, label, placeholder }) => (
                  <div key={key} className="flex flex-col gap-1">
                    <label htmlFor={key} className="text-xs font-medium text-ink-faint">
                      {label}
                    </label>
                    <input
                      id={key}
                      value={filters[key]}
                      onChange={(e) => setFilters((f) => ({ ...f, [key]: e.target.value }))}
                      placeholder={placeholder}
                      disabled={isSubmitting}
                      className="rounded-lg border border-border bg-paper px-3 py-2 text-sm text-ink placeholder:text-ink-faint transition-colors focus:border-violet focus:outline-none focus:ring-2 focus:ring-violet-light disabled:opacity-60"
                    />
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <button
        type="submit"
        disabled={isSubmitting || !name.trim()}
        className="flex items-center justify-center gap-2 rounded-xl bg-coral px-4 py-3.5 text-base font-semibold text-paper transition-colors hover:bg-coral-dark disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
            Searching…
          </>
        ) : (
          "Search"
        )}
      </button>
    </motion.form>
  );
}
