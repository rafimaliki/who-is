import type { Candidate, ProfileResponse, SearchRequest, SearchResponse } from "./types";

// Stubs docs/API_CONTRACT.md's two endpoints with fixture data + fake latency so the full
// frontend flow can be built and clicked through before the backend exists. Swapping to real
// `fetch` calls later means replacing the bodies of these two functions only — call sites and
// return shapes stay identical.

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/** Rotating status lines the UI cycles through while a mock call is "in flight". */
export const THINKING_MESSAGES = {
  search: [
    "Searching public sources…",
    "Scanning search-indexed social profiles…",
    "Cross-referencing results…",
    "Clustering distinct people…",
  ],
  profile: [
    "Reviewing the chosen candidate…",
    "Fetching public pages…",
    "Extracting sourced facts…",
    "Verifying every citation…",
  ],
};

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pick<T>(arr: T[]): T {
  return arr[randomInt(0, arr.length - 1)]!;
}

/** Illustrated (not real-photo) avatars — matches the app's own stance on not normalizing real face scraping, even in mock data. */
function avatarUrl(seed: string): string {
  return `https://api.dicebear.com/9.x/notionists/svg?seed=${encodeURIComponent(seed)}`;
}

const OCCUPATIONS = [
  "software engineer",
  "attorney",
  "high school teacher",
  "restaurant owner",
  "graphic designer",
  "registered nurse",
  "marketing manager",
  "electrician",
];

const CITIES = ["Seattle", "Chicago", "Austin", "Denver", "Portland", "Raleigh", "Phoenix", "Columbus"];

function generateCandidates(name: string, count: number): Candidate[] {
  const used = new Set<string>();
  const candidates: Candidate[] = [];

  for (let i = 0; i < count; i++) {
    let occupation = pick(OCCUPATIONS);
    let city = pick(CITIES);
    let attempts = 0;
    while (used.has(`${occupation}|${city}`) && attempts < 10) {
      occupation = pick(OCCUPATIONS);
      city = pick(CITIES);
      attempts++;
    }
    used.add(`${occupation}|${city}`);

    const id = `gen_${i}_${Math.random().toString(36).slice(2, 8)}`;
    const confidence = Math.max(0.32, 0.93 - i * 0.16 - Math.random() * 0.06);

    candidates.push({
      id,
      label: `${name}, ${occupation}, ${city}`,
      summary: `Works as a ${occupation}, based in ${city}.`,
      photo_url: Math.random() < 0.5 ? avatarUrl(id) : null,
      confidence: Number(confidence.toFixed(2)),
    });
  }

  return candidates.sort((a, b) => b.confidence - a.confidence);
}

const AMBIGUOUS_CANDIDATES: Candidate[] = [
  {
    id: "c_1",
    label: "John Smith, software engineer, Seattle",
    summary: "Backend engineer at Acme Corp, based in Seattle since 2019.",
    photo_url: avatarUrl("c_1"),
    confidence: 0.82,
  },
  {
    id: "c_2",
    label: "John Smith, attorney, Chicago",
    summary: "Corporate lawyer at a Chicago firm, active in local bar association.",
    photo_url: null,
    confidence: 0.71,
  },
  {
    id: "c_3",
    label: "John Smith, musician, Austin",
    summary: "Session guitarist and part-time producer, several regional tour credits.",
    photo_url: avatarUrl("c_3"),
    confidence: 0.64,
  },
];

const PROFILE_FIXTURE: ProfileResponse = {
  profile_id: "p_xyz789",
  fields: {
    full_name: "Jonathan A. Smith",
    aliases: ["Jon Smith"],
    location_current: "Seattle, WA",
    location_history: ["Chicago, IL"],
    occupation: "Software Engineer",
    employer: "Acme Corp",
    education: [{ institution: "University of Washington", degree: "BS, Computer Science", year: 2015 }],
    social_profiles: [
      { platform: "github", url: "https://github.com/jsmith", confidence: 0.9 },
      { platform: "linkedin", url: "https://linkedin.com/in/jonathan-a-smith", confidence: 0.88 },
      { platform: "x", url: "https://x.com/jsmithdev", confidence: 0.62 },
    ],
    photos: [avatarUrl("jonathan-a-smith")],
    summary:
      "Jonathan Smith is a software engineer based in Seattle, currently working on backend systems at Acme Corp. Previously based in Chicago; graduated from the University of Washington in 2015.",
  },
  sources: [
    {
      url: "https://acmecorp.example/team/jonathan-smith",
      title: "Acme Corp — Engineering Team",
      snippet: "Jonathan Smith joined Acme Corp's backend team in 2019, based in our Seattle office.",
      supports_field: "employer",
    },
    {
      url: "https://acmecorp.example/team/jonathan-smith",
      title: "Acme Corp — Engineering Team",
      snippet: "Jonathan Smith joined Acme Corp's backend team in 2019, based in our Seattle office.",
      supports_field: "location_current",
    },
    {
      url: "https://linkedin.com/in/jonathan-a-smith",
      title: "Jonathan A. Smith | LinkedIn",
      snippet: "BS Computer Science, University of Washington, 2015. Also goes by Jon Smith.",
      supports_field: "education",
    },
    {
      url: "https://linkedin.com/in/jonathan-a-smith",
      title: "Jonathan A. Smith | LinkedIn",
      snippet: "BS Computer Science, University of Washington, 2015. Also goes by Jon Smith.",
      supports_field: "aliases",
    },
    {
      url: "https://github.com/jsmith",
      title: "jsmith (Jonathan Smith) · GitHub",
      snippet: "Backend engineer. Seattle, WA. Previously Chicago, IL.",
      supports_field: "location_history",
    },
    {
      url: "https://acmecorp.example/team/jonathan-smith",
      title: "Acme Corp — Engineering Team",
      snippet: "Jonathan works as a Software Engineer on the backend infrastructure team.",
      supports_field: "occupation",
    },
    {
      url: "https://github.com/jsmith",
      title: "jsmith (Jonathan Smith) · GitHub",
      snippet: "Personal site links to LinkedIn and X profiles.",
      supports_field: "social_profiles",
    },
  ],
};

/** Dev-only trigger words in the `name` field, for exercising specific states reliably. */
const DEV_TRIGGERS = {
  ambiguous: "john smith",
  empty: "test empty",
  error: "test error",
};

export async function searchPerson(req: SearchRequest): Promise<SearchResponse> {
  await delay(1600);

  const trimmed = req.name.trim();
  const name = trimmed.toLowerCase();

  if (name === DEV_TRIGGERS.error) {
    throw { error: "upstream_error", message: "search API or LLM call failed" };
  }

  if (name === DEV_TRIGGERS.empty) {
    return { search_id: "s_empty", candidates: [], auto_selected: false };
  }

  if (name === DEV_TRIGGERS.ambiguous) {
    return { search_id: "s_abc123", candidates: AMBIGUOUS_CANDIDATES, auto_selected: false };
  }

  // A first-name-only search collides with far more real people than a full name does —
  // weight the odds of an ambiguous result accordingly, same logic an OSINT tool actually needs.
  const wordCount = trimmed.split(/\s+/).filter(Boolean).length;
  const ambiguousChance = wordCount <= 1 ? 0.6 : 0.15;
  const isAmbiguous = Math.random() < ambiguousChance;

  if (isAmbiguous) {
    const candidates = generateCandidates(trimmed, randomInt(2, 4));
    return { search_id: `s_${Date.now()}`, candidates, auto_selected: false };
  }

  const [single] = generateCandidates(trimmed, 1);
  return { search_id: `s_${Date.now()}`, candidates: [single!], auto_selected: true };
}

export async function selectCandidate(_searchId: string, _candidateId: string): Promise<ProfileResponse> {
  await delay(2400);
  return PROFILE_FIXTURE;
}
