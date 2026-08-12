"""Request/response shapes for the API — mirrors docs/API_CONTRACT.md and docs/DATA_MODEL.md.

Keep in sync with frontend/src/lib/types.ts; that file mirrors the same two docs independently.
"""

from typing import Literal

from pydantic import BaseModel, Field

SocialPlatform = Literal[
    "instagram", "facebook", "x", "linkedin", "tiktok", "youtube", "github", "other"
]

ErrorCode = Literal["not_found", "validation_error", "upstream_error", "rate_limited"]


class SearchRequest(BaseModel):
    name: str = Field(min_length=1)
    country: str | None = None
    age_range: str | None = None
    occupation: str | None = None
    aliases: list[str] | None = None


class Candidate(BaseModel):
    id: str
    label: str
    summary: str
    photo_url: str | None
    confidence: float


class SearchResponse(BaseModel):
    search_id: str
    candidates: list[Candidate]
    auto_selected: bool


class SelectRequest(BaseModel):
    candidate_id: str


class SocialProfile(BaseModel):
    platform: SocialPlatform
    url: str
    confidence: float


class Education(BaseModel):
    institution: str
    degree: str | None
    year: int | None


class ProfileFields(BaseModel):
    full_name: str
    aliases: list[str]
    location_current: str | None
    location_history: list[str]
    occupation: str | None
    employer: str | None
    education: list[Education]
    social_profiles: list[SocialProfile]
    photos: list[str]
    summary: str


class Source(BaseModel):
    url: str
    title: str
    snippet: str
    supports_field: str


class ProfileResponse(BaseModel):
    profile_id: str
    fields: ProfileFields
    sources: list[Source]


class ApiErrorBody(BaseModel):
    error: ErrorCode
    message: str
