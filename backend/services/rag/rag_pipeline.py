from __future__ import annotations

from pathlib import Path
import json

from services.rag.retriever import retrieve
from services.rag.self_consistency import compute_confidence
from services.rag.hallucination_check import hallucination_check

PROMPT_TEMPLATE = Path("prompts/rag_lab_explainer.txt").read_text(encoding="utf-8")


def _normalize(x: str) -> str:
    return (x or "").strip().lower()


def filter_retrieved_chunks(patient_result: dict, retrieved: list[dict], top_k: int = 3) -> list[dict]:
    test_name = _normalize(patient_result.get("test", ""))
    filtered = []

    for chunk in retrieved:
        meta = chunk.get("metadata", {})
        title = _normalize(meta.get("title", meta.get("label", "")))
        text = _normalize(chunk.get("text", ""))
        combined = f"{title} {text}"

        score = 0
        for token in test_name.split():
            if token and token in combined:
                score += 1

        filtered.append((score, chunk))

    filtered.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in filtered[:top_k]]


def build_prompt(patient_result: dict, retrieved_chunks: list[dict]) -> str:
    evidence_lines = []
    for i, chunk in enumerate(retrieved_chunks, start=1):
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        title = meta.get("title", meta.get("label", "untitled"))
        evidence_lines.append(f"[{i}] ({source}) {title}: {chunk.get('text', '')}")

    return PROMPT_TEMPLATE.format(
        patient_result=json.dumps(patient_result, ensure_ascii=False),
        evidence="\n".join(evidence_lines)
    )


def parse_json_safely(text: str) -> dict:
    try:
        data = json.loads(text)
        return {
            "status": data.get("status", "unknown"),
            "explanation": data.get("explanation", "The result could not be confidently interpreted."),
            "evidence_used": data.get("evidence_used", []),
        }
    except Exception:
        return {
            "status": "unknown",
            "explanation": "The result could not be confidently interpreted.",
            "evidence_used": [],
        }


def call_llm_multiple_times(prompt: str, llm_callable, n: int = 5):
    outputs = []
    for _ in range(n):
        raw = llm_callable(prompt)
        outputs.append(parse_json_safely(raw))
    return outputs


def compress_evidence(chunks: list[dict], max_items: int = 3) -> list[dict]:
    out = []
    for c in chunks[:max_items]:
        meta = c.get("metadata", {})
        out.append({
            "source": meta.get("source", "unknown"),
            "title": meta.get("title", meta.get("label", "untitled")),
            "snippet": c.get("text", "")[:180],
        })
    return out


def apply_guardrails(conf: dict, hallucination: dict, retrieved: list[dict], samples: list[dict], patient_result: dict) -> dict:
    final_status = conf.get("final_status") or "unknown"
    explanation = samples[0].get("explanation", "The result could not be confidently interpreted.")
    needs_manual_review = False

    no_evidence = not retrieved
    low_conf = conf.get("confidence_band") == "low"
    low_vote = conf.get("vote_ratio", 0.0) < 0.60
    very_low_agreement = conf.get("semantic_agreement", 0.0) < 0.50
    hallucinated = hallucination.get("hallucination_flag", False)

    if no_evidence or low_conf or low_vote or very_low_agreement or hallucinated:
        final_status = "unknown"
        needs_manual_review = True
        explanation = "The available evidence is insufficient to support a confident interpretation."

    # Slightly less conservative than before: if confidence is moderate, evidence supported,
    # and agreement is acceptable, preserve the model's status.
    if (
        conf.get("confidence_band") == "moderate"
        and conf.get("semantic_agreement", 0.0) >= 0.50
        and conf.get("vote_ratio", 0.0) >= 0.60
        and not hallucinated
        and retrieved
    ):
        needs_manual_review = False

    return {
        "final_status": final_status,
        "final_explanation": explanation,
        "needs_manual_review": needs_manual_review,
    }


def run_rag_pipeline(patient_result: dict, llm_callable):
    query = f"{patient_result.get('test','')} {patient_result.get('value','')} {patient_result.get('unit','')} {patient_result.get('reference','')}"
    retrieved_raw = retrieve(query, top_k=6)
    retrieved = filter_retrieved_chunks(patient_result, retrieved_raw, top_k=3)

    prompt = build_prompt(patient_result, retrieved)
    samples = call_llm_multiple_times(prompt, llm_callable, n=5)
    confidence = compute_confidence(samples)

    evidence_chunks = [x.get("text", "") for x in retrieved]
    hallucination = hallucination_check(
        explanation=samples[0].get("explanation", ""),
        evidence_chunks=evidence_chunks,
        threshold=0.33,
    )

    guarded = apply_guardrails(confidence, hallucination, retrieved, samples, patient_result)

    return {
        "retrieved_evidence": compress_evidence(retrieved, max_items=3),
        "samples": samples,
        "final_status": guarded["final_status"],
        "final_explanation": guarded["final_explanation"],
        "needs_manual_review": guarded["needs_manual_review"],
        "confidence": confidence,
        "hallucination": hallucination,
    }
