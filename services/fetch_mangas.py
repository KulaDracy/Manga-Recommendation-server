import json
import os
from fastapi import HTTPException, Request
from embedding.Generate_candiate import generate_candidates
from embedding.Re_ranking import recommend_from_multiple_mangas, load_cache_from_disk
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_FILE = os.path.join(PROJECT_DIR, "manga_data.json")
load_cache_from_disk()


SENSITIVE_TAGS = {"horror", "sexual violence", "gore", "boys' love", "girls' love", "doujinshi"}
SENSITIVE_KEYWORDS = {"succubus", "doujinshi", "ntr", "slave", "enslave", "succusbus", "sex", "boobs", "kill", "killed"}

def is_sensitive(manga):
    tags = set(tag.lower() for tag in manga.get("tag", []))
    if tags & SENSITIVE_TAGS:
        return True
    title = manga.get("title", "").lower()
    desc = manga.get("description", "").lower()
    for kw in SENSITIVE_KEYWORDS:
        if kw in title or kw in desc:
            return True
    return False

def parse_manga_ids_from_cookie(request: Request):
    raw_cookie = request.cookies.get("manga_ids")
    if not raw_cookie:
        return []
    
    try:
        decoded = urllib.parse.unquote(raw_cookie)
        print("Decoded cookie:", decoded)
        manga_ids = json.loads(decoded)
        if isinstance(manga_ids, list):
            return manga_ids
        print("Dữ liệu sau decode không phải list.")
    except Exception as e:
        print("Lỗi parse cookie:", e)
    
    return []


def fetch_mangas(request: Request, page: int = 1, limit: int = 20):
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="File dữ liệu manga không tồn tại.")

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_mangas = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Lỗi khi đọc file JSON.")

    # Tách non-sensitive, sensitive, suggestive
    non_sensitive, sensitive, suggestive_or_erotica = [], [], []

    for manga in all_mangas:
        rating = manga.get("content_rating", "").lower()
        if rating in {"erotica", "suggestive"}:
            suggestive_or_erotica.append(manga)
        elif is_sensitive(manga):
            sensitive.append(manga)
        else:
            non_sensitive.append(manga)

    sorted_all = non_sensitive + sensitive + suggestive_or_erotica
    manga_dict = {m["id"]: m for m in sorted_all}

    
    manga_ids = parse_manga_ids_from_cookie(request)
    print("Manga IDs from cookie:", manga_ids)
   
    viewed_mangas = [manga_dict[mid] for mid in manga_ids if mid in manga_dict]

    
    recommended_ids = set()
    recommended_candidates = recommend_from_multiple_mangas([m["id"] for m in viewed_mangas])
    recommended_ids = [r["id"] for r in recommended_candidates]
    recommended_mangas = [manga_dict[rid] for rid in recommended_ids if rid in manga_dict]

    
    displayed_ids = set(m["id"] for m in viewed_mangas + recommended_mangas)
    remaining_mangas = [m for m in sorted_all if m["id"] not in displayed_ids]
    
    print("Manga IDs from cookie:", manga_ids)

    
    final_mangas = viewed_mangas + recommended_mangas + remaining_mangas

    
    total = len(final_mangas)
    total_pages = (total + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit
    paginated = final_mangas[start:end]

    
    simplified = []
    for manga in paginated:
        rating = manga.get("content_rating", "").lower()
        simplified.append({
            "id": manga["id"],
            "title": manga["title"],
            "author": manga.get("author", "Unknown"),
            "description": manga.get("description", "No description available."),
            "status": manga.get("status", "unknown"),
            "tags": manga.get("tag", []),
            "coverUrl": manga.get("cover_image", "https://via.placeholder.com/100x150"),
            "backgroundUrl": manga.get("background_image", "https://via.placeholder.com/800x400"),
            "createdAt": manga.get("created_at", "Unknown"),
            "updatedAt": manga.get("updated_at", "Unknown"),
            "views": manga.get("views", 0),
            "contentRating": rating
        })

    return {
        "mangas": simplified,
        "total": total,
        "totalPages": total_pages
    }
