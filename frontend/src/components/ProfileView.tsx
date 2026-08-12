import type { ProfileResponse } from "../lib/types";

// PLACEHOLDER — functional but minimally styled. Replaced by the ProfileView feature branch with
// a proper field grid and expandable source citations. Keep the props contract stable.

interface ProfileViewProps {
  profile: ProfileResponse;
  onNewSearch: () => void;
}

export function ProfileView({ profile, onNewSearch }: ProfileViewProps) {
  const { fields, sources } = profile;

  return (
    <div className="flex flex-col gap-4">
      <h2 className="font-display text-2xl">{fields.full_name}</h2>
      <p className="text-ink-soft">{fields.summary}</p>
      <ul className="flex flex-col gap-2 text-sm">
        {Object.entries(fields)
          .filter(([key, value]) => key !== "full_name" && key !== "summary" && value)
          .map(([key, value]) => (
            <li key={key} className="rounded-lg border border-border bg-paper px-3 py-2">
              <strong className="mr-2">{key}:</strong>
              <span>{Array.isArray(value) ? JSON.stringify(value) : String(value)}</span>
            </li>
          ))}
      </ul>
      <p className="text-xs text-ink-faint">{sources.length} sources cited</p>
      <button type="button" onClick={onNewSearch} className="self-start text-sm text-violet">
        New search
      </button>
    </div>
  );
}
