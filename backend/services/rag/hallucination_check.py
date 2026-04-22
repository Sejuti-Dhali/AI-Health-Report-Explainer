from __future__ import annotations

from difflib import SequenceMatcher


def _normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _best_similarity(explanation: str, evidence_chunks: list[str]) -> float:
    exp = _normalize(explanation)
    if not exp or not evidence_chunks:
        return 0.0

    best = 0.0
    for chunk in evidence_chunks:
        ch = _normalize(chunk)
        if not ch:
            continue
        score = SequenceMatcher(None, exp, ch).ratio()
        if score > best:
            best = score
    return best


def is_supported(explanation: str, evidence_chunks: list[str], threshold: float = 0.33) -> bool:
    return _best_similarity(explanation, evidence_chunks) >= threshold


def hallucination_check(explanation: str, evidence_chunks: list[str], threshold: float = 0.33) -> dict:
    best = _best_similarity(explanation, evidence_chunks)
    supported = best >= threshold
    return {
        "is_supported": supported,
        "hallucination_flag": not supported,
        "evidence_support_score": round(best, 3),
        "evidence_support": supported,
    }
