// Shapes mirror .docs/API_CONTRACT.md and .docs/DATA_MODEL.md — keep in sync when the backend lands.

export interface SearchRequest {
  name: string;
  country?: string;
  age_range?: string;
  occupation?: string;
  aliases?: string[];
}

export interface Candidate {
  id: string;
  label: string;
  summary: string;
  photo_url: string | null;
  confidence: number;
}

export interface SearchResponse {
  search_id: string;
  candidates: Candidate[];
  auto_selected: boolean;
}

export type SocialPlatform =
  | "instagram"
  | "facebook"
  | "x"
  | "linkedin"
  | "tiktok"
  | "youtube"
  | "github"
  | "other";

export interface SocialProfile {
  platform: SocialPlatform;
  url: string;
  confidence: number;
}

export interface Education {
  institution: string;
  degree: string | null;
  year: number | null;
}

export interface ProfileFields {
  full_name: string;
  aliases: string[];
  location_current: string | null;
  location_history: string[];
  occupation: string | null;
  employer: string | null;
  education: Education[];
  social_profiles: SocialProfile[];
  photos: string[];
  summary: string;
}

export interface Source {
  url: string;
  title: string;
  snippet: string;
  supports_field: string;
}

export interface ProfileResponse {
  profile_id: string;
  fields: ProfileFields;
  sources: Source[];
}

export interface ApiError {
  error: "not_found" | "validation_error" | "upstream_error" | "rate_limited";
  message: string;
}
