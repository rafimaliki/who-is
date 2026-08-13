"""API response shape for the profile domain — mirrors .docs/API_CONTRACT.md."""

from pydantic import BaseModel

from app.shared.types import ProfileFields, Source


class ProfileResponse(BaseModel):
    profile_id: str
    fields: ProfileFields
    sources: list[Source]
