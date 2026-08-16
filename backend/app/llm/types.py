"""OpenRouter I/O shapes — kept separate from the API's own types (app/search/types.py,
app/profile/types.py). The LLM's candidate output carries `source_urls` for grounding, which the
API's Candidate never exposes to the frontend; llm/service.py's caller maps between the two."""

from pydantic import BaseModel

from app.shared.types import SocialPlatform


class ClusterCandidate(BaseModel):
    label: str
    summary: str
    photo_url: str | None = None
    confidence: float
    source_urls: list[str]


class ClusterOutput(BaseModel):
    candidates: list[ClusterCandidate]


class ExtractEducation(BaseModel):
    institution: str
    degree: str | None = None
    year: int | None = None


class ExtractSocialProfile(BaseModel):
    platform: SocialPlatform
    url: str
    confidence: float


class ExtractFields(BaseModel):
    full_name: str
    aliases: list[str]
    location_current: str | None = None
    location_history: list[str]
    occupation: str | None = None
    employer: str | None = None
    education: list[ExtractEducation]
    social_profiles: list[ExtractSocialProfile]
    photos: list[str]
    summary: str


class ExtractSource(BaseModel):
    url: str
    title: str
    snippet: str
    supports_field: str


class ExtractOutput(BaseModel):
    fields: ExtractFields
    sources: list[ExtractSource]
