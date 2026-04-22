from services.rag.chroma_store import get_collection
from services.rag.embedder import embed_query

def retrieve(query, top_k=5):
    col = get_collection()
    emb = embed_query(query)
    res = col.query(query_embeddings=[emb], n_results=top_k)

    docs = res["documents"][0]
    metas = res["metadatas"][0]

    return [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
