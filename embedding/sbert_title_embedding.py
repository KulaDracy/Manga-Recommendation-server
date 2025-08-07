from sentence_transformers import SentenceTransformer
import json
import os

INPUT_FILE = "manga_data.json"
ITEM_PROFILE_FILE = "manga_title_tag_embedding.json"

class SBERTEmbedding:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def encode_text(self, text):
        return self.model.encode(text).tolist()

def load_existing_profiles():
    if os.path.exists(ITEM_PROFILE_FILE):
        with open(ITEM_PROFILE_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                existing_ids = {item["id"] for item in data}
                return existing_ids, data
            except json.JSONDecodeError:
                print("Lỗi đọc file title_tag_embedding.json, tạo mới.")
    return set(), []

def load_manga_data():
    if not os.path.exists(INPUT_FILE):
        print(f"Không tìm thấy file {INPUT_FILE}")
        return []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_item_profiles():
    existing_ids, existing_profiles = load_existing_profiles()
    all_manga = load_manga_data()

    sbert = SBERTEmbedding()
    new_profiles = []

    for manga in all_manga:
        if manga["id"] in existing_ids:
            continue

        title = manga.get("title", "")
        tags = manga.get("tag", [])
        tag_text = " ".join(tags)

        combined_text = f"{title} {tag_text}".strip()
        embedding = sbert.encode_text(combined_text)

        new_profiles.append({
            "id": manga["id"],
            "title": title,
            "tags": tags,
            "embedding": embedding
        })

    total_profiles = existing_profiles + new_profiles

    with open(ITEM_PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(total_profiles, f, ensure_ascii=False, indent=4)

    print(f"Đã thêm {len(new_profiles)} manga mới. Tổng cộng: {len(total_profiles)}")

if __name__ == "__main__":
    generate_item_profiles()
