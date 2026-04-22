from __future__ import annotations

import csv
import sys
from pathlib import Path

# ---- fix import path ----
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.rag.rag_pipeline import run_rag_pipeline


def dummy_llm(prompt: str) -> str:
    return '{"status":"unknown","explanation":"The available evidence is insufficient to support a confident interpretation.","evidence_used":["dummy"]}'


def compute_summary(rows: list[dict]) -> dict:
    total = len(rows)
    exact = sum(1 for r in rows if r["expected_status"] == r["predicted_status"])
    abstentions = sum(1 for r in rows if r["predicted_status"] == "unknown")
    hallucinations = sum(1 for r in rows if str(r["hallucination_flag"]).lower() == "true")
    manual_reviews = sum(1 for r in rows if str(r["needs_manual_review"]).lower() == "true")

    return {
        "total_cases": total,
        "exact_match": exact,
        "exact_match_rate": round(exact / total, 3) if total else 0.0,
        "abstentions": abstentions,
        "abstention_rate": round(abstentions / total, 3) if total else 0.0,
        "hallucination_flags": hallucinations,
        "manual_reviews": manual_reviews,
    }


def run_cases(cases: list[dict], llm_callable, out_csv: str = "data/rag/eval_results.csv", summary_txt: str = "data/rag/eval_summary.txt"):
    rows = []
    for case in cases:
        result = run_rag_pipeline(case, llm_callable)
        conf = result["confidence"]
        hall = result["hallucination"]

        rows.append({
            "case_id": case.get("case_id", ""),
            "test": case.get("test", ""),
            "value": case.get("value", ""),
            "unit": case.get("unit", ""),
            "reference": case.get("reference", ""),
            "expected_status": case.get("expected_status", ""),
            "predicted_status": result.get("final_status", "unknown"),
            "confidence_score": conf.get("confidence", 0.0),
            "confidence_band": conf.get("confidence_band", "low"),
            "vote_ratio": conf.get("vote_ratio", 0.0),
            "semantic_agreement": conf.get("semantic_agreement", 0.0),
            "needs_manual_review": result.get("needs_manual_review", False),
            "hallucination_flag": hall.get("hallucination_flag", False),
            "evidence_support": hall.get("evidence_support", False),
            "evidence_support_score": hall.get("evidence_support_score", 0.0),
        })

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    summary = compute_summary(rows)
    with open(summary_txt, "w", encoding="utf-8") as f:
        for k, v in summary.items():
            f.write(f"{k}: {v}\n")

    print(f"Saved CSV to {out_csv}")
    print(f"Saved summary to {summary_txt}")
    print(summary)


if __name__ == "__main__":
    demo_cases = [
        {"case_id":"1","test":"Hemoglobin","value":"12.5","unit":"g/dL","reference":"13.0 - 17.0 g/dL","expected_status":"low"},
        {"case_id":"2","test":"WBC COUNT","value":"9000","unit":"cumm","reference":"4.5-11.0 thousand/uL","expected_status":"normal"},
        {"case_id":"3","test":"PLATELET COUNT","value":"150000","unit":"cumm","reference":"150-400 thousand/uL","expected_status":"normal"},
        {"case_id":"4","test":"MCV","value":"87.75","unit":"fL","reference":"83 - 101","expected_status":"normal"},
        {"case_id":"5","test":"MCHC","value":"32.8","unit":"g/dL","reference":"32-36 g/dL","expected_status":"normal"},
    ]
    run_cases(demo_cases, dummy_llm)
