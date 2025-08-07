import httpx
import asyncio

MANGADEX_API = "https://api.mangadex.org/manga"

async def get_manga_with_most_tags(limit=100, max_pages=10):
    offset = 0
    most_tags_count = 0
    manga_with_most_tags = None

    async with httpx.AsyncClient() as client:
        for page in range(max_pages):
            params = {
                "limit": limit,
                "offset": offset,
                "availableTranslatedLanguage[]": "en"
            }

            response = await client.get(MANGADEX_API, params=params)
            if response.status_code != 200:
                print(f"Lỗi khi lấy dữ liệu: {response.status_code}")
                break

            data = response.json().get("data", [])
            if not data:
                break

            for manga in data:
                tags = manga["attributes"].get("tags", [])
                num_tags = len(tags)

                if num_tags > most_tags_count:
                    most_tags_count = num_tags
                    manga_with_most_tags = {
                        "id": manga["id"],
                        "title": manga["attributes"]["title"].get("en", "No title"),
                        "num_tags": num_tags,
                        "tag_names": [tag["attributes"]["name"]["en"] for tag in tags]
                    }

            offset += limit

    return manga_with_most_tags

if __name__ == "__main__":
    result = asyncio.run(get_manga_with_most_tags())

    if result:
        print("\nManga có nhiều tag nhất:")
        print(f"ID: {result['id']}")
        print(f"Title: {result['title']}")
        print(f"Số lượng tag: {result['num_tags']}")
        print(f"Tags: {', '.join(result['tag_names'])}")
    else:
        print("Không tìm thấy manga nào.")
