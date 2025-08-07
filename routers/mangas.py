from fastapi import APIRouter, HTTPException, Query, Request
from services.fetch_mangas import fetch_mangas
from services.fetch_manga_detail import fetch_manga_detail
from services.fetch_mangaChapter import fetch_manga_chapters
from pydantic import BaseModel
from embedding.Re_ranking import re_rank_candidates
from services.fetch_chapter import fetch_chapter_pages

router = APIRouter()

@router.get("/mangas")
@router.get("/mangas")
async def get_mangas(
    request: Request,  
    page: int = Query(1, gt=0),
    limit: int = Query(20, gt=0, le=100)
):
    return fetch_mangas(request=request, page=page, limit=limit)

@router.get("/mangas/{manga_id}")
async def get_manga_detail(manga_id: str):
    detail = await fetch_manga_detail(manga_id)
    recommendations = re_rank_candidates(manga_id)
    return {"manga": detail, "recommendations": recommendations}

@router.get("/mangas/{manga_id}/chapters")
async def get_chapters(manga_id: str):
    chapters = await fetch_manga_chapters(manga_id)
    return {"chapters": chapters}

@router.get("/mangas/{manga_id}/chapters/{chapter_id}")
async def get_chapter_pages(chapter_id: str):
    return fetch_chapter_pages(chapter_id)

class MultiRecommendationRequest(BaseModel):
    manga_ids: list[str]
    top_k_each: int = 20

@router.get("/mangas/{manga_id}/more_recommendations")
def get_more_recs(manga_id: str, offset: int = 0, limit: int = 100):
    _, _, candidates = re_rank_candidates(manga_id)  
    return candidates[offset : offset + limit]


