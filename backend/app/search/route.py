"""Routes for the search domain — .docs/API_CONTRACT.md's search + select endpoints. Business
logic lives in service.py; handlers here only translate HTTP <-> that logic."""

from fastapi import APIRouter

from app.profile.types import ProfileResponse

from . import service
from .types import SearchRequest, SearchResponse, SelectRequest

router = APIRouter(prefix="/api")


@router.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest) -> SearchResponse:
    trimmed = req.name.strip()
    filters = {
        "country": req.country,
        "age_range": req.age_range,
        "occupation": req.occupation,
        "aliases": req.aliases,
    }
    return await service.run_search(trimmed, filters)


@router.post("/search/{search_id}/select", response_model=ProfileResponse)
async def select(search_id: str, req: SelectRequest) -> ProfileResponse:
    return await service.run_select(search_id, req.candidate_id)
