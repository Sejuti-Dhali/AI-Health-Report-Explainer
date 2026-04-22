import json
from pathlib import Path
import chromadb
from services.rag.embedder import embed_texts

DB_DIR = "data/rag/chroma_db"
COLLECTION_NAME = "medical_rag"

def get_collection():
    Path(DB_DIR).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_or_create_collection(name=COLLECTION_NAME)

def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def build_index(paths):
    collection = get_collection()
    all_rows = []
    for path in paths:
        all_rows.extend(load_jsonl(path))

    docs = [r["text"] for r in all_rows]
    ids = [r["id"] for r in all_rows]
    metas = [{k: str(v) for k, v in r.items() if k != "text"} for r in all_rows]

    embeddings = embed_texts(docs)

    collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)
    return len(ids)
