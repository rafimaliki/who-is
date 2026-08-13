"""API request/response shapes for the search domain — mirrors .docs/API_CONTRACT.md."""

from pydantic import BaseModel, Field


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
