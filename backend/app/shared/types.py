"""Types genuinely shared across domain modules — the search and profile domains both reference
these, per .docs/DATA_MODEL.md's entity model (a Profile's fields/sources aren't search-specific,
a Candidate isn't profile-specific, but the field-level shapes below are used by both)."""

from typing import Literal

from pydantic import BaseModel

SocialPlatform = Literal[
    "instagram", "facebook", "x", "linkedin", "tiktok", "youtube", "github", "other"
]

ErrorCode = Literal["not_found", "validation_error", "upstream_error", "rate_limited"]


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


class ApiErrorBody(BaseModel):
    error: ErrorCode
    message: str
