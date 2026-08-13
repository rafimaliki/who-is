import type { ApiError, ProfileResponse, SearchRequest, SearchResponse } from "./types";

/** The app's one dependency on "however we find people" — swap the implementation, not the callers. */
export interface PersonSearchService {
  search(req: SearchRequest): Promise<SearchResponse>;
  select(searchId: string, candidateId: string): Promise<ProfileResponse>;
}

const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseErrorBody(res: Response): Promise<ApiError> {
  try {
    const body = await res.json();
    if (body && typeof body.error === "string" && typeof body.message === "string") {
      return body as ApiError;
    }
  } catch {
    // fall through to the generic shape below
  }
  return { error: "upstream_error", message: `Request failed (${res.status})` };
}

/** Talks to the FastAPI backend over HTTP, per docs/API_CONTRACT.md. */
export class HttpPersonSearchService implements PersonSearchService {
  constructor(private readonly baseUrl: string) {}

  async search(req: SearchRequest): Promise<SearchResponse> {
    const res = await this.post("/api/search", req);
    if (!res.ok) throw await parseErrorBody(res);
    return res.json();
  }

  async select(searchId: string, candidateId: string): Promise<ProfileResponse> {
    const res = await this.post(`/api/search/${encodeURIComponent(searchId)}/select`, {
      candidate_id: candidateId,
    });
    if (!res.ok) throw await parseErrorBody(res);
    return res.json();
  }

  private async post(path: string, body: unknown): Promise<Response> {
    try {
      return await fetch(`${this.baseUrl}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    } catch {
      // Developer-facing detail only — App.tsx's toSafeMessage() logs this and shows the user
      // curated copy instead, never this string directly.
      const unreachable: ApiError = {
        error: "upstream_error",
        message: `Network error reaching ${this.baseUrl}${path}`,
      };
      throw unreachable;
    }
  }
}

export const personSearchService: PersonSearchService = new HttpPersonSearchService(API_BASE_URL);
