import requests
from fastapi import HTTPException

def fetch_chapter_pages(chapter_id: str):
    base_url = f"https://api.mangadex.org/at-home/server/{chapter_id}"
    headers = {
        "User-Agent": "MyMangaApp/1.0 (https://example.com)"
    }

    res = requests.get(base_url, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail="Không thể lấy nội dung chương truyện.")

    data = res.json()
    if "chapter" not in data:
        raise HTTPException(status_code=500, detail="Dữ liệu chapter không hợp lệ.")

    host = data["baseUrl"]
    chapter_hash = data["chapter"]["hash"]
    pages = data["chapter"]["data"]

    image_urls = [f"{host}/data/{chapter_hash}/{file}" for file in pages]

    return {
        "chapterId": chapter_id,
        "title": data["chapter"].get("title", "Untitled"),
        "pages": image_urls
    }
