import requests
import json
import os
from datetime import datetime

MANGADEX_API_URL = "https://api.mangadex.org/manga"
AUTHOR_API_URL = "https://api.mangadex.org/author"
COVER_API_URL = "https://uploads.mangadex.org/covers/"
DATA_FILE = "test_data.json"

def format_date(iso_date):
    if iso_date:
        return datetime.fromisoformat(iso_date.replace("Z", "")).strftime("%d/%m/%Y")
    return "Không xác định"

def load_existing_manga():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("File JSON lỗi hoặc trống, tạo mới.")
    return []

def get_author_name(author_id):
    try:
        response = requests.get(f"{AUTHOR_API_URL}/{author_id}")
        if response.status_code == 200:
            data = response.json()
            return data["data"]["attributes"].get("name", "Không rõ")
    except Exception as e:
        print(f"Lỗi khi lấy tác giả {author_id}: {e}")
    return "Không rõ"

def get_all_manga(batch_size=100):
    existing_manga = load_existing_manga()
    existing_ids = {m["id"] for m in existing_manga}

    manga_list = existing_manga.copy()
    offset = 0
    new_added = 0

    while True:
        params = {
            "limit": batch_size,
            "offset": offset,
            "includes[]": ["cover_art", "author"]
        }

        response = requests.get(MANGADEX_API_URL, params=params)
        if response.status_code != 200:
            print(f"Lỗi khi lấy dữ liệu: {response.status_code}")
            break

        data = response.json()
        manga_data = data.get("data", [])
        total = data.get("total", 0)

        if not manga_data:
            break

        for manga in manga_data:
            manga_id = manga["id"]
            if manga_id in existing_ids:
                continue

            attributes = manga["attributes"]
            title = attributes["title"].get("en", "Không có tiêu đề")
            description = attributes["description"].get("en", "Không có mô tả")
            tags = [tag["attributes"]["name"]["en"] for tag in attributes["tags"]]
            created_at = format_date(attributes.get("createdAt"))
            updated_at = format_date(attributes.get("updatedAt"))
            status = attributes.get("status", "Không rõ")
            language = attributes.get("originalLanguage", "Không rõ")
            content_rating = attributes.get("contentRating", "Không rõ")
            demographic = attributes.get("publicationDemographic", "Không rõ")
            year = attributes.get("year", "Không rõ")
            last_chapter = attributes.get("lastChapter", "Không rõ")
            last_volume = attributes.get("lastVolume", "Không rõ")
            available_languages = attributes.get("availableTranslatedLanguages", [])

            cover_image = None
            author_name = "Không rõ"

            for relation in manga["relationships"]:
                if relation["type"] == "cover_art":
                    cover_image = f"{COVER_API_URL}{manga_id}/{relation['attributes']['fileName']}"
                elif relation["type"] == "author":
                    author_id = relation["id"]
                    author_name = get_author_name(author_id)

            background_image = f"https://source.unsplash.com/random/800x400?anime={title.replace(' ', '%20')}"

            manga_list.append({
                "id": manga_id,
                "title": title,
                "author": author_name,
                "description": description,
                "cover_image": cover_image,
                "background_image": background_image,
                "tag": tags,
                "created_at": created_at,
                "updated_at": updated_at,
                "status": status,
                "language": language,
                "content_rating": content_rating,
                "demographic": demographic,
                "year": year,
                "last_chapter": last_chapter,
                "last_volume": last_volume,
                "available_languages": available_languages
            })

            existing_ids.add(manga_id)
            new_added += 1

        print(f"Đã xử lý {offset + len(manga_data)} / {total}")
        offset += batch_size

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(manga_list, file, ensure_ascii=False, indent=4)

        if len(manga_data) < batch_size:
            break

    manga_list.sort(key=lambda x: datetime.strptime(x["updated_at"], "%d/%m/%Y") if x["updated_at"] != "Không xác định" else datetime.min,
                    reverse=True)

    return manga_list, new_added

if __name__ == "__main__":
    mangas, new_manga_count = get_all_manga()

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(mangas, file, ensure_ascii=False, indent=4)

    print(f"\nĐã thêm {new_manga_count} manga mới.")
    print(f"Tổng cộng có {len(mangas)} manga trong {DATA_FILE}.")
