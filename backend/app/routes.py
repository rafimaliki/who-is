"""Routes for docs/API_CONTRACT.md's three endpoints. Business logic lives in stub.py — handlers
here only translate HTTP <-> that logic."""

from fastapi import APIRouter, HTTPException

from .models import ProfileResponse, SearchRequest, SearchResponse, SelectRequest
from .stub import get_profile, run_search, run_select

router = APIRouter(prefix="/api")


@router.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest) -> SearchResponse:
    trimmed = req.name.strip()
    return await run_search(trimmed.lower(), trimmed)


@router.post("/search/{search_id}/select", response_model=ProfileResponse)
async def select(search_id: str, req: SelectRequest) -> ProfileResponse:
    return await run_select(search_id, req.candidate_id)


@router.get("/profile/{profile_id}", response_model=ProfileResponse)
async def get_profile_by_id(profile_id: str) -> ProfileResponse:
    profile = get_profile(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=404, detail={"error": "not_found", "message": "profile_id does not exist"}
        )
    return profile
