from services.rag.chroma_store import build_index

if __name__ == "__main__":
    paths = [
        "data/rag/pubmed_abstracts.jsonl",
        "data/rag/loinc_terms.jsonl",
        "data/rag/snomed_terms.jsonl"
    ]
    n = build_index(paths)
    print(f"Indexed {n} documents.")
