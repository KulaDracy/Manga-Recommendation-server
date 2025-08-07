import os
import json
from .Generate_candiate import generate_candidates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
RECOMMENDATION_CACHE = {}

CACHE_FILE = os.path.join(PROJECT_ROOT, "recommendation_cache.json")


def re_rank_candidates(manga_id):
    if manga_id in RECOMMENDATION_CACHE:
        top_5, temp, candidates = RECOMMENDATION_CACHE[manga_id]
        return top_5, temp, candidates

    candidates = generate_candidates(manga_id, top_k=100)
    top_5 = candidates[:5]
    temp = candidates[5:]

    RECOMMENDATION_CACHE[manga_id] = (top_5, temp, candidates)
    save_cache_to_disk()
    return top_5, temp, candidates
    


def recommend_from_multiple_mangas(manga_ids):
    recommended = []
    seen_ids = set()
    for mid in manga_ids:
        try:
            top_5, _, _ = re_rank_candidates(mid)
            for m in top_5:
                if m["id"] not in seen_ids:
                    recommended.append(m)
                    seen_ids.add(m["id"])
        except Exception as e:
            print(f"Lỗi khi gợi ý từ manga {mid}: {e}")
            continue

    return recommended


def save_cache_to_disk():
    try:
        serializable_cache = {
            manga_id: data[2] 
            for manga_id, data in RECOMMENDATION_CACHE.items()
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(serializable_cache, f, ensure_ascii=False, indent=2)
        print("✅ Cache đã được lưu vào đĩa.")
    except Exception as e:
        print("Lỗi khi lưu cache:", e)


def load_cache_from_disk():
    global RECOMMENDATION_CACHE
    if not os.path.exists(CACHE_FILE):
        return

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            raw_cache = json.load(f)
            for manga_id, candidates in raw_cache.items():
                top_5 = candidates[:5]
                temp = candidates[5:]
                RECOMMENDATION_CACHE[manga_id] = (top_5, temp, candidates)
        print("Cache đã được load từ đĩa.")
    except Exception as e:
        print("Lỗi khi load cache:", e)
