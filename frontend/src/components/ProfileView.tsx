import { ArrowLeft, ExternalLink } from "lucide-react";
import type { ProfileResponse } from "../lib/types";
import { ProfileField } from "./ProfileField";

interface ProfileViewProps {
  profile: ProfileResponse;
  onNewSearch: () => void;
}

// ponytail: lucide-react 1.31 dropped its trademarked brand glyphs (no Github/Linkedin/Youtube
// export left to import), so every platform falls back to the generic external-link icon the
// brief specifies for platforms without a dedicated one. Swap in brand icons if the dep upgrades.

export function ProfileView({ profile, onNewSearch }: ProfileViewProps) {
  const { fields, sources } = profile;
  const sourcesFor = (key: string) => sources.filter((s) => s.supports_field === key);

  const initials = fields.full_name
    .split(/\s+/)
    .map((part) => part[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <div className="flex flex-col gap-6 animate-fade-up">
      <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
        <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-coral-light font-display text-2xl font-semibold text-coral-dark">
          {initials || "?"}
        </div>
        <div className="min-w-0">
          <h2 className="font-display text-3xl leading-tight text-ink sm:text-4xl">{fields.full_name}</h2>
          {(fields.occupation || fields.employer) && (
            <p className="mt-1 text-sm text-ink-soft">
              {fields.occupation}
              {fields.occupation && fields.employer ? " at " : ""}
              {fields.employer}
            </p>
          )}
        </div>
      </div>

      <p className="leading-relaxed text-ink-soft">{fields.summary}</p>

      <div className="flex flex-col gap-3">
        {fields.aliases.length > 0 && (
          <ProfileField label="Also known as" sources={sourcesFor("aliases")}>
            {fields.aliases.join(", ")}
          </ProfileField>
        )}

        {fields.location_current && (
          <ProfileField label="Current location" sources={sourcesFor("location_current")}>
            {fields.location_current}
          </ProfileField>
        )}

        {fields.location_history.length > 0 && (
          <ProfileField label="Past locations" sources={sourcesFor("location_history")}>
            {fields.location_history.join(", ")}
          </ProfileField>
        )}

        {fields.occupation && (
          <ProfileField label="Occupation" sources={sourcesFor("occupation")}>
            {fields.occupation}
          </ProfileField>
        )}

        {fields.employer && (
          <ProfileField label="Employer" sources={sourcesFor("employer")}>
            {fields.employer}
          </ProfileField>
        )}

        {fields.education.length > 0 && (
          <ProfileField label="Education" sources={sourcesFor("education")}>
            <ul className="flex flex-col gap-1">
              {fields.education.map((edu, i) => (
                <li key={i}>
                  {edu.institution}
                  {edu.degree ? ` — ${edu.degree}` : ""}
                  {edu.year ? ` (${edu.year})` : ""}
                </li>
              ))}
            </ul>
          </ProfileField>
        )}

        {fields.social_profiles.length > 0 && (
          <ProfileField label="Social profiles" sources={sourcesFor("social_profiles")}>
            <ul className="flex flex-col gap-2">
              {fields.social_profiles.map((sp) => (
                <li key={sp.url}>
                  <a
                    href={sp.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 text-ink transition-colors hover:text-coral"
                  >
                    <ExternalLink className="h-4 w-4 shrink-0 text-ink-faint" aria-hidden="true" />
                    <span className="truncate">{sp.url.replace(/^https?:\/\//, "")}</span>
                  </a>
                </li>
              ))}
            </ul>
          </ProfileField>
        )}
      </div>

      <p className="text-xs text-ink-faint">
        {sources.length} source{sources.length === 1 ? "" : "s"} cited across this profile.
      </p>

      <button
        type="button"
        onClick={onNewSearch}
        className="inline-flex w-fit items-center gap-1 text-sm font-medium text-violet transition-colors hover:text-violet-dark"
      >
        <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
        New search
      </button>
    </div>
  );
}
