from transformers import BertTokenizer, BertModel
import torch
import json
import os

INPUT_FILE = "manga_data.json"
TAG_EMBEDDING_FILE = "manga_tag_embeddings.json"

class BERTEmbedding:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.model = BertModel.from_pretrained("bert-base-uncased")
        self.model.eval()

    def encode_text(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.squeeze(0)
            mean_embedding = embeddings.mean(dim=0)
            return mean_embedding.tolist()

def load_tags_from_file():
    if not os.path.exists(INPUT_FILE):
        print(f"Không tìm thấy file {INPUT_FILE}")
        return []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        manga_list = json.load(f)

    seen_tags = set()
    for manga in manga_list:
        tags = manga.get("tag", [])
        for tag in tags:
            if tag:
                seen_tags.add(tag)

    return list(seen_tags)

def generate_tag_embeddings():
    if os.path.exists(TAG_EMBEDDING_FILE):
        with open(TAG_EMBEDDING_FILE, "r", encoding="utf-8") as f:
            existing_embeddings = json.load(f)
    else:
        existing_embeddings = {}

    print("Đang đọc danh sách tag từ file manga_data.json...")
    tags = load_tags_from_file()
    print(f"Tổng số tag thu thập được: {len(tags)}")

    bert = BERTEmbedding()
    updated = 0

    for tag in tags:
        if tag not in existing_embeddings:
            embedding = bert.encode_text(tag)
            existing_embeddings[tag] = embedding
            updated += 1
            print(f"Đã tạo vector cho tag: {tag}")

    with open(TAG_EMBEDDING_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_embeddings, f, ensure_ascii=False, indent=4)

    print(f"Đã cập nhật {updated} tag mới. Tổng cộng: {len(existing_embeddings)}")

if __name__ == "__main__":
    generate_tag_embeddings()
