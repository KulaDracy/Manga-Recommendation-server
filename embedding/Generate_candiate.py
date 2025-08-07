import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDING_DIR = os.path.join(BASE_DIR)
TAG_EMBEDDING_FILE = os.path.join(EMBEDDING_DIR, "manga_tag_embeddings.json")
MANGA_DATA_FILE = os.path.join(EMBEDDING_DIR, "manga_data.json") 
TITLE_EMBEDDING_FILE = os.path.join(EMBEDDING_DIR, "manga_title_tag_embedding.json")
DESCIPTION_EMBEDDING_FILE = os.path.join(EMBEDDING_DIR,"manga_describe_embedding.json")
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def mean_embedding_from_tags(tags, tag_embeddings):
    vectors = []
    for tag in tags:
        if tag in tag_embeddings:
            vectors.append(tag_embeddings[tag])
    if not vectors:
        return None  
    return np.mean(np.array(vectors), axis=0)

def generate_candidates(manga_id, top_k=50, save_to_file=None):
    tag_embeddings = load_json(TAG_EMBEDDING_FILE)
    raw_title_embeddings = load_json(TITLE_EMBEDDING_FILE)
    manga_data = load_json(MANGA_DATA_FILE)
    raw_desc_embeddings = load_json(DESCIPTION_EMBEDDING_FILE)
    desc_embeddings = {
        item["id"]: item["embedding"] for item in raw_desc_embeddings
    }
    title_embeddings = {
        item["id"]: item["embedding"] for item in raw_title_embeddings
    }
    
    # Lấy ra manga đầu vào
    input_manga = next((m for m in manga_data if m["id"] == manga_id), None)
    if not input_manga:
        print(f"Manga ID {manga_id} không tìm thấy.")
        return []

    input_tags = input_manga.get("tag", [])
    input_vector = mean_embedding_from_tags(input_tags, tag_embeddings)
    input_title_vector = title_embeddings.get(manga_id)
    input_desc_vector = desc_embeddings.get(manga_id)


    if input_vector is None or input_title_vector is None or input_desc_vector is None:
        print(f"Không có đủ embedding cho manga {manga_id}")
        return []

    candidates = []
    for manga in manga_data:
        if manga["id"] == manga_id:
            continue  # Bỏ qua chính nó

        target_tags = manga.get("tag", [])
        target_vector = mean_embedding_from_tags(target_tags, tag_embeddings)
        target_title_vector = title_embeddings.get(manga["id"])
        target_desc_vector = desc_embeddings.get(manga["id"])

        if target_vector is None or target_title_vector is None or target_desc_vector is None:
            continue

        tag_sim = cosine_similarity([input_vector], [target_vector])[0][0]
        title_sim = cosine_similarity([input_title_vector], [target_title_vector])[0][0]
        desc_sim = cosine_similarity([input_desc_vector], [target_desc_vector])[0][0]

        combined_sim = (tag_sim + title_sim +  desc_sim)/3

        candidates.append({
            "id": manga["id"],
            "title": manga.get("title"),
            "coverUrl": manga.get("cover_image"),
            "similarity": combined_sim,
            "status": manga.get("status"),
            "tags": manga.get("tag")
        })

    return sorted(candidates, key=lambda x: x["similarity"], reverse=True)[:top_k]
