import re
from typing import Optional, Tuple, List, Dict

from prompts.reference_ranges import get_range

ALIASES = {
    "hb": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "haemoglobin": "hemoglobin",
    "wbc": "wbc",
    "total wbc count": "wbc",
    "rbc": "rbc",
    "platelet count": "platelets",
    "platelets": "platelets",
    "mcv": "mcv",
    "mch": "mch",
    "mchc": "mchc",
    "glucose": "glucose_random",
    "fasting glucose": "glucose_fasting",
    "hba1c": "hba1c",
    "creatinine": "creatinine",
    "sodium": "sodium",
    "potassium": "potassium",
    "calcium": "calcium",
    "total cholesterol": "total_cholesterol",
    "ldl": "ldl",
    "hdl": "hdl",
    "triglycerides": "triglycerides",
    "alt": "alt",
    "ast": "ast",
    "bilirubin": "bilirubin_total",
    "albumin": "albumin",
    "tsh": "tsh",
    "t3": "t3",
    "t4": "t4",
}


def normalize_name(name: str) -> str:
    key = name.strip().lower()
    return ALIASES.get(key, key.replace(" ", "_"))


def extract_numeric(value: str) -> Optional[float]:
    if value is None:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(match.group()) if match else None


def compare_to_range(name: str, value: str, gender: str = "general") -> Tuple[str, Optional[str]]:
    norm = normalize_name(name)
    range_info = get_range(norm, gender)
    numeric = extract_numeric(value)

    if not range_info or numeric is None or not range_info.get("range"):
        return "unknown", None

    low, high = range_info["range"]
    unit = range_info.get("unit")
    ref_text = f"{low}-{high} {unit}" if unit else f"{low}-{high}"

    if numeric < low:
        return "low", ref_text
    if numeric > high:
        return "high", ref_text
    return "normal", ref_text


def clinical_explanation(name: str, status: str, value: str, ref_text: Optional[str]) -> str:
    if status == "normal":
        return f"{name} is within the expected reference range" + (f" ({ref_text})" if ref_text else "") + "."
    if status == "low":
        return f"{name} is below the expected reference range" + (f" ({ref_text})" if ref_text else "") + ". Clinical correlation is recommended."
    if status == "high":
        return f"{name} is above the expected reference range" + (f" ({ref_text})" if ref_text else "") + ". Clinical correlation is recommended."
    return f"{name} could not be confidently interpreted from the extracted report text."


def summarize_risk(parameters: List[Dict]) -> Dict:
    high_count = sum(1 for p in parameters if p.get("status") == "high")
    low_count = sum(1 for p in parameters if p.get("status") == "low")
    abnormal_count = high_count + low_count

    if abnormal_count == 0:
        return {
            "level": "Low",
            "summary": "No clearly abnormal values were identified among the extracted parameters.",
            "recommendations": [
                "Review the full report with a clinician if symptoms are present."
            ],
        }

    if abnormal_count <= 2:
        return {
            "level": "Moderate",
            "summary": "A small number of extracted values appear to be outside the expected range and may need medical review.",
            "recommendations": [
                "Discuss the abnormal values with a qualified clinician.",
                "Interpret results together with symptoms and clinical history.",
            ],
        }

    return {
        "level": "High",
        "summary": "Multiple extracted values appear to be outside the expected range. Medical review is advisable.",
        "recommendations": [
            "Seek medical review, especially if symptoms are present.",
            "Do not make treatment decisions based only on this AI summary.",
        ],
    }
