from services.rag.retriever import retrieve

res = retrieve("Hemoglobin 12.5 g/dL CBC low", top_k=5)
for i, r in enumerate(res, 1):
    print(f"\n--- {i} ---")
    print(r["metadata"])
    print(r["text"][:300])
