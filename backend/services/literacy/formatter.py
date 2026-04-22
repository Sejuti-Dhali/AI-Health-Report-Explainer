import re
from typing import Dict

def _clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()

def _sentence_count(text: str) -> int:
    count = len(re.findall(r"[.!?]+", text or ""))
    return max(1, count)

def _word_list(text: str):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text or "")

def _count_syllables_in_word(word: str) -> int:
    word = (word or "").lower()
    if not word:
        return 1

    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False

    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel

    if word.endswith("e") and count > 1:
        count -= 1

    return max(1, count)

def flesch_kincaid_grade_level(text: str) -> float:
    text = _clean_spaces(text)
    if not text:
        return 0.0

    words = _word_list(text)
    word_count = max(1, len(words))
    sentence_count = _sentence_count(text)
    syllable_count = sum(_count_syllables_in_word(w) for w in words)

    fkgl = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
    return round(max(0.0, fkgl), 2)

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
        ("manual review is recommended", "a doctor should review this"),
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

    fkgl = flesch_kincaid_grade_level(out)

    if level == "layperson":
        readability_band = "easy"
        readability_auto_check = fkgl <= 8.0
    elif level == "intermediate":
        readability_band = "moderate"
        readability_auto_check = fkgl <= 12.0
    else:
        readability_band = "technical"
        readability_auto_check = True

    return {
        "formatted_text": out,
        "literacy_level": level,
        "readability_metric": "FKGL",
        "readability_score": fkgl,
        "readability_band": readability_band,
        "readability_auto_check": readability_auto_check
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
    item["readability_metric"] = primary["readability_metric"]
    item["readability_score"] = primary["readability_score"]
    item["readability_band"] = primary["readability_band"]
    item["readability_auto_check"] = primary["readability_auto_check"]

    return item
