from collections import Counter
from difflib import SequenceMatcher

def normalize_label(text):
    return (text or "").strip().lower()

def majority_vote(labels):
    norm = [normalize_label(x) for x in labels if x]
    if not norm:
        return None, 0.0
    c = Counter(norm)
    label, count = c.most_common(1)[0]
    return label, count / len(norm)

def semantic_agreement(texts):
    texts = [t.strip().lower() for t in texts if t and t.strip()]
    if len(texts) < 2:
        return 0.0
    sims = []
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            sims.append(SequenceMatcher(None, texts[i], texts[j]).ratio())
    return sum(sims) / len(sims) if sims else 0.0

def compute_confidence(samples):
    statuses = [x.get("status", "") for x in samples]
    explanations = [x.get("explanation", "") for x in samples]

    voted_status, vote_ratio = majority_vote(statuses)
    agreement = semantic_agreement(explanations)
    confidence = 0.6 * vote_ratio + 0.4 * agreement

    if confidence >= 0.80:
        band = "high"
    elif confidence >= 0.55:
        band = "moderate"
    else:
        band = "low"

    return {
        "final_status": voted_status,
        "vote_ratio": round(vote_ratio, 3),
        "semantic_agreement": round(agreement, 3),
        "confidence": round(confidence, 3),
        "confidence_band": band,
    }
