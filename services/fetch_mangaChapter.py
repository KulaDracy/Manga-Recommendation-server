import requests

async def fetch_manga_chapters(manga_id: str):
    CHAPTER_API_URL = f"https://api.mangadex.org/manga/{manga_id}/feed"
    limit = 100  
    offset = 0
    all_chapters = []

    while True:
        params = {
            "translatedLanguage[]": "en",
            "limit": limit,
            "offset": offset,
            "order[createdAt]": "desc"
        }

        response = requests.get(CHAPTER_API_URL, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch chapters: {response.status_code}")

        data = response.json()
        chapters = data.get("data", [])
        if not chapters:
            break

        for chap in chapters:
            all_chapters.append({
                "id": chap["id"],
                "title": chap["attributes"].get("title", "Untitled"),
                "chapter": chap["attributes"].get("chapter", "Unknown"),
                "createdAt": chap["attributes"].get("createdAt", None)
            })
        if len(chapters) < limit:
            break

        offset += limit

    return all_chapters
