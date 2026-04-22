from sentence_transformers import SentenceTransformer

_MODEL = None

def get_embedder():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _MODEL

def embed_texts(texts):
    return get_embedder().encode(texts, normalize_embeddings=True).tolist()

def embed_query(text):
    return get_embedder().encode([text], normalize_embeddings=True)[0].tolist()
