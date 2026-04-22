import json
from services.rag.rag_pipeline import run_rag_pipeline

def dummy_llm(prompt):
    if "Hemoglobin" in prompt or '"test": "Hb"' in prompt:
        return '{"status":"low","explanation":"The value appears below the retrieved reference interval.","evidence_used":["pubmed","loinc"]}'
    if "WBC COUNT" in prompt and "9000" in prompt:
        return '{"status":"unknown","explanation":"The unit presentation may require manual checking before safe interpretation.","evidence_used":["loinc"]}'
    if "WBC COUNT" in prompt:
        return '{"status":"normal","explanation":"The value appears within the retrieved adult reference interval.","evidence_used":["pubmed","loinc"]}'
    if "PLATELET COUNT" in prompt:
        return '{"status":"normal","explanation":"The value appears at the lower boundary of the retrieved reference interval.","evidence_used":["pubmed"]}'
    return '{"status":"unknown","explanation":"The result could not be confidently interpreted.","evidence_used":[]}'

with open("data/rag/manual_benchmark.jsonl", "r", encoding="utf-8-sig") as f:
    for line in f:
        if not line.strip():
            continue
        case = json.loads(line)
        out = run_rag_pipeline(case, dummy_llm)
        print("\n==============================")
        print("CASE:", case["case"])
        print("EXPECTED:", case["expected_status"])
        print("FINAL STATUS:", out["final_status"])
        print("CONF:", out["confidence"])
        print("EXPLANATION:", out["final_explanation"])
        print("MANUAL REVIEW:", out["needs_manual_review"])
        print("TOP EVIDENCE:", out["retrieved_evidence"][:2])
