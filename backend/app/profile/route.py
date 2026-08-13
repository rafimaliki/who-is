"""Routes for the profile domain — .docs/API_CONTRACT.md's GET /api/profile/{id}."""

from fastapi import APIRouter, HTTPException

from . import service
from .types import ProfileResponse

router = APIRouter(prefix="/api")


@router.get("/profile/{profile_id}", response_model=ProfileResponse)
async def get_profile_by_id(profile_id: str) -> ProfileResponse:
    profile = service.get_profile(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=404, detail={"error": "not_found", "message": "profile_id does not exist"}
        )
    return profile
