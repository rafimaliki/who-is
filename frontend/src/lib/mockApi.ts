import type { Candidate, ProfileResponse, SearchRequest, SearchResponse } from "./types";

// Stubs docs/API_CONTRACT.md's two endpoints with fixture data + fake latency so the full
// frontend flow can be built and clicked through before the backend exists. Swapping to real
// `fetch` calls later means replacing the bodies of these two functions only — call sites and
// return shapes stay identical.

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const AMBIGUOUS_CANDIDATES: Candidate[] = [
  {
    id: "c_1",
    label: "John Smith, software engineer, Seattle",
    summary: "Backend engineer at Acme Corp, based in Seattle since 2019.",
    photo_url: null,
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
    photo_url: null,
    confidence: 0.64,
  },
];

const SINGLE_CANDIDATE: Candidate = {
  id: "c_solo",
  label: "Jonathan A. Smith, software engineer, Seattle",
  summary: "Backend engineer at Acme Corp, based in Seattle since 2019.",
  photo_url: null,
  confidence: 0.94,
};

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
    photos: [],
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
  ],
};

/** Dev-only trigger words in the `name` field, for exercising states with no backend yet. */
const DEV_TRIGGERS = {
  ambiguous: "john smith",
  empty: "test empty",
  error: "test error",
};

export async function searchPerson(req: SearchRequest): Promise<SearchResponse> {
  await delay(900);

  const name = req.name.trim().toLowerCase();

  if (name === DEV_TRIGGERS.error) {
    throw { error: "upstream_error", message: "search API or LLM call failed" };
  }

  if (name === DEV_TRIGGERS.empty) {
    return { search_id: "s_empty", candidates: [], auto_selected: false };
  }

  if (name === DEV_TRIGGERS.ambiguous) {
    return { search_id: "s_abc123", candidates: AMBIGUOUS_CANDIDATES, auto_selected: false };
  }

  return { search_id: "s_solo456", candidates: [SINGLE_CANDIDATE], auto_selected: true };
}

export async function selectCandidate(_searchId: string, _candidateId: string): Promise<ProfileResponse> {
  await delay(1400);
  return PROFILE_FIXTURE;
}
