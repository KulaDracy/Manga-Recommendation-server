import json
import os
from datetime import datetime
from fastapi import HTTPException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR) 
DATA_FILE = os.path.join(PROJECT_DIR, "manga_data.json")

async def fetch_manga_detail(manga_id: str):
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="File dữ liệu manga không tồn tại.")
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            all_mangas = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Lỗi khi đọc file JSON.")

    manga = next((m for m in all_mangas if m["id"] == manga_id), None)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")

    title = manga["title"]
    description = manga["description"]
    status = manga.get("status", "Unknown")
    tags = manga.get("tag", [])
    created_at = manga.get("created_at", "Unknown")

    try:
        year = datetime.strptime(created_at, "%d/%m/%Y").year
    except (ValueError, TypeError):
        year = "Unknown Year"

    publication_demographic = manga.get("demographic", "Unknown")
    original_language = manga.get("language", "Unknown")
    updated_at = manga.get("updated_at", "Unknown")
    cover_url = manga.get("cover_image", "https://via.placeholder.com/100x150")
    author = manga.get("author", "Unknown")
    external_links = []

    return {
        "id": manga_id,
        "title": title,
        "description": description,
        "status": status,
        "tags": tags,
        "author": author,
        "year": year,
        "publicationDemographic": publication_demographic,
        "originalLanguage": original_language,
        "createdAt": created_at,
        "updatedAt": updated_at,
        "coverUrl": cover_url,
        "externalLinks": external_links
    }
