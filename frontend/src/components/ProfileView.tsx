import type { ReactNode } from "react";
import { motion } from "motion/react";
import { ArrowLeft, ExternalLink } from "lucide-react";
import type { ProfileResponse, Source } from "../lib/types";
import { ProfileField } from "./ProfileField";

interface ProfileViewProps {
  profile: ProfileResponse;
  onNewSearch: () => void;
}

// ponytail: lucide-react 1.31 dropped its trademarked brand glyphs (no Github/Linkedin/Youtube
// export left to import), so every platform falls back to the generic external-link icon the
// brief specifies for platforms without a dedicated one. Swap in brand icons if the dep upgrades.

interface FieldEntry {
  key: string;
  label: string;
  sources: Source[];
  content: ReactNode;
}

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

  const entries: FieldEntry[] = [];

  if (fields.aliases.length > 0) {
    entries.push({ key: "aliases", label: "Also known as", sources: sourcesFor("aliases"), content: fields.aliases.join(", ") });
  }
  if (fields.location_current) {
    entries.push({ key: "location_current", label: "Current location", sources: sourcesFor("location_current"), content: fields.location_current });
  }
  if (fields.location_history.length > 0) {
    entries.push({ key: "location_history", label: "Past locations", sources: sourcesFor("location_history"), content: fields.location_history.join(", ") });
  }
  if (fields.occupation) {
    entries.push({ key: "occupation", label: "Occupation", sources: sourcesFor("occupation"), content: fields.occupation });
  }
  if (fields.employer) {
    entries.push({ key: "employer", label: "Employer", sources: sourcesFor("employer"), content: fields.employer });
  }
  if (fields.education.length > 0) {
    entries.push({
      key: "education",
      label: "Education",
      sources: sourcesFor("education"),
      content: (
        <ul className="flex flex-col gap-1">
          {fields.education.map((edu, i) => (
            <li key={i}>
              {edu.institution}
              {edu.degree ? ` — ${edu.degree}` : ""}
              {edu.year ? ` (${edu.year})` : ""}
            </li>
          ))}
        </ul>
      ),
    });
  }
  if (fields.social_profiles.length > 0) {
    entries.push({
      key: "social_profiles",
      label: "Social profiles",
      sources: sourcesFor("social_profiles"),
      content: (
        <ul className="flex flex-col gap-2">
          {fields.social_profiles.map((sp) => (
            <li key={sp.url}>
              <a
                href={sp.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 text-ink transition-colors hover:text-indigo"
              >
                <ExternalLink className="h-4 w-4 shrink-0 text-ink-faint" aria-hidden="true" />
                <span className="truncate font-mono">{sp.url.replace(/^https?:\/\//, "")}</span>
              </a>
            </li>
          ))}
        </ul>
      ),
    });
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="flex flex-col gap-6"
    >
      <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
        {fields.photos[0] ? (
          <img
            src={fields.photos[0]}
            alt=""
            className="h-16 w-16 shrink-0 rounded-md border-[1.5px] border-ink object-cover"
          />
        ) : (
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-md border-[1.5px] border-ink bg-indigo-tint font-display text-2xl font-bold text-indigo-dark">
            {initials || "?"}
          </div>
        )}
        <div className="min-w-0">
          <h2 className="font-display text-3xl leading-tight font-bold text-ink sm:text-4xl">{fields.full_name}</h2>
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
        {entries.map((entry, i) => (
          <motion.div
            key={entry.key}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: 0.15 + i * 0.06, ease: [0.16, 1, 0.3, 1] }}
          >
            <ProfileField label={entry.label} sources={entry.sources}>
              {entry.content}
            </ProfileField>
          </motion.div>
        ))}
      </div>

      <p className="font-mono text-xs text-ink-faint">
        {sources.length} source{sources.length === 1 ? "" : "s"} cited across this profile.
      </p>

      <button
        type="button"
        onClick={onNewSearch}
        className="inline-flex w-fit items-center gap-1 text-sm font-medium text-indigo transition-colors hover:text-indigo-dark"
      >
        <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
        New search
      </button>
    </motion.div>
  );
}
