import { useState, type FormEvent } from "react";
import type { SearchRequest } from "../lib/types";

// PLACEHOLDER — functional but minimally styled. Replaced by the SearchForm feature branch with
// full filter fields, validation, and motion. Keep the props contract (onSubmit/isSubmitting)
// stable so App.tsx doesn't need to change.

interface SearchFormProps {
  onSubmit: (req: SearchRequest) => void;
  isSubmitting: boolean;
}

export function SearchForm({ onSubmit, isSubmitting }: SearchFormProps) {
  const [name, setName] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    onSubmit({ name: name.trim() });
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <h1 className="font-display text-3xl">Who is…</h1>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Full name"
        disabled={isSubmitting}
        className="rounded-xl border border-border bg-paper px-4 py-3"
      />
      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-xl bg-coral px-4 py-3 font-medium text-paper disabled:opacity-60"
      >
        {isSubmitting ? "Searching…" : "Search"}
      </button>
    </form>
  );
}
