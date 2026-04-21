import re
from typing import Dict

def _clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()

def simple_readability_score(text: str) -> float:
    text = _clean_spaces(text)
    if not text:
        return 0.0
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    words = re.findall(r"\b[\w'-]+\b", text)
    word_count = max(1, len(words))
    avg_sentence_len = word_count / sentences
    long_words = sum(1 for w in words if len(w) >= 7)
    long_word_ratio = long_words / word_count
    score = 100 - (avg_sentence_len * 1.8) - (long_word_ratio * 35)
    return round(max(0.0, min(100.0, score)), 2)

def _to_layperson_english(text: str) -> str:
    t = _clean_spaces(text)
    replacements = [
        ("appears within the expected contextual interval", "looks within the normal range"),
        ("appears above the expected contextual interval", "looks higher than the normal range"),
        ("appears below the expected contextual interval", "looks lower than the normal range"),
        ("Clinical correlation is recommended.", "Please interpret this together with symptoms and a doctor's advice."),
        ("contextual interval", "normal range"),
        ("reference interval", "normal range"),
        ("contextual range", "normal range"),
        ("clinical review is recommended", "a doctor should review this"),
    ]
    for a, b in replacements:
        t = re.sub(a, b, t, flags=re.IGNORECASE)
    return t

def _to_intermediate_english(text: str) -> str:
    t = _clean_spaces(text)
    replacements = [
        ("contextual interval", "reference range"),
        ("contextual range", "reference range"),
        ("Clinical correlation is recommended.", "Clinical review is recommended."),
    ]
    for a, b in replacements:
        t = re.sub(a, b, t, flags=re.IGNORECASE)
    return t

def _to_clinical_english(text: str) -> str:
    return _clean_spaces(text)

def format_explanation(text: str, literacy_level: str = "layperson") -> Dict:
    level = (literacy_level or "layperson").strip().lower()
    base = _clean_spaces(text)

    if level == "clinical":
        out = _to_clinical_english(base)
    elif level == "intermediate":
        out = _to_intermediate_english(base)
    else:
        out = _to_layperson_english(base)

    readability = simple_readability_score(out)

    if level == "layperson":
        readability_band = "easy"
    elif level == "intermediate":
        readability_band = "moderate"
    else:
        readability_band = "technical"

    return {
        "formatted_text": out,
        "literacy_level": level,
        "readability_score": readability,
        "readability_band": readability_band,
        "readability_auto_check": readability >= 55 if level == "layperson" else True
    }

def apply_literacy_controls(item: dict, literacy_level: str = "layperson") -> dict:
    primary = format_explanation(
        item.get("explanation", ""),
        literacy_level=literacy_level
    )
    personal = format_explanation(
        item.get("personalized_explanation", ""),
        literacy_level=literacy_level
    )

    item["explanation"] = primary["formatted_text"]
    item["personalized_explanation"] = personal["formatted_text"]
    item["literacy_level"] = literacy_level
    item["readability_score"] = primary["readability_score"]
    item["readability_band"] = primary["readability_band"]
    item["readability_auto_check"] = primary["readability_auto_check"]

    return item
