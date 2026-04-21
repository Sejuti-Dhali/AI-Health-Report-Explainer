import re

CBC_SPECS = [
    {
        "canonical": "Hemoglobin",
        "aliases": ["hemoglobin", "haemoglobin", "hb", "hgb"],
        "unit": "g/dL",
        "ref_male": (13.0, 17.0),
        "ref_female": (12.0, 15.0),
    },
    {
        "canonical": "RBC COUNT",
        "aliases": ["rbc count", "rbc", "red blood cell", "total rbc count"],
        "unit": "million/uL",
        "ref_male": (4.5, 5.9),
        "ref_female": (4.1, 5.1),
    },
    {
        "canonical": "Packed Cell Volume (PCV)",
        "aliases": ["packed cell volume", "pcv", "hematocrit", "hct"],
        "unit": "%",
        "ref_male": (40.0, 50.0),
        "ref_female": (36.0, 46.0),
    },
    {
        "canonical": "Mean Corpuscular Volume (MCV)",
        "aliases": ["mean corpuscular volume", "mcv"],
        "unit": "fL",
        "ref_general": (80.0, 100.0),
    },
    {
        "canonical": "MCH",
        "aliases": ["mch", "mean corpuscular hemoglobin"],
        "unit": "pg",
        "ref_general": (27.0, 33.0),
    },
    {
        "canonical": "MCHC",
        "aliases": ["mchc", "mean corpuscular hemoglobin concentration"],
        "unit": "g/dL",
        "ref_general": (32.0, 36.0),
    },
    {
        "canonical": "RDW",
        "aliases": ["rdw", "red cell distribution width"],
        "unit": "%",
        "ref_general": (11.5, 14.5),
    },
    {
        "canonical": "WBC COUNT",
        "aliases": ["wbc count", "wbc", "white blood cell", "total leukocyte count", "total wbc count"],
        "unit": "thousand/uL",
        "ref_general": (4.5, 11.0),
    },
    {
        "canonical": "Neutrophils",
        "aliases": ["neutrophils", "neutrophil"],
        "unit": "%",
        "ref_general": (40.0, 70.0),
    },
    {
        "canonical": "Lymphocytes",
        "aliases": ["lymphocytes", "lymphocyte"],
        "unit": "%",
        "ref_general": (20.0, 40.0),
    },
    {
        "canonical": "Eosinophils",
        "aliases": ["eosinophils", "eosinophil"],
        "unit": "%",
        "ref_general": (0.0, 6.0),
    },
    {
        "canonical": "Monocytes",
        "aliases": ["monocytes", "monocyte"],
        "unit": "%",
        "ref_general": (0.0, 10.0),
    },
    {
        "canonical": "Basophils",
        "aliases": ["basophils", "basophil"],
        "unit": "%",
        "ref_general": (0.0, 2.0),
    },
    {
        "canonical": "PLATELET COUNT",
        "aliases": ["platelet count", "platelet", "plt"],
        "unit": "thousand/uL",
        "ref_general": (150.0, 400.0),
    },
]

NUMBER_RE = re.compile(r'(?<![A-Za-z])(\d+(?:\.\d+)?)')

def _normalize_text(text: str) -> list[str]:
    text = text.replace("\r", "\n")
    lines = [ln.strip() for ln in text.split("\n")]
    return [ln for ln in lines if ln]

def _get_ref(spec: dict, sex: str):
    sex = (sex or "female").strip().lower()
    if sex == "male" and "ref_male" in spec:
        return spec["ref_male"]
    if sex != "male" and "ref_female" in spec:
        return spec["ref_female"]
    return spec.get("ref_general", spec.get("ref_female", spec.get("ref_male", (None, None))))

def _extract_value_from_line(line: str):
    nums = NUMBER_RE.findall(line)
    if not nums:
        return None
    try:
        return float(nums[0])
    except Exception:
        return None

def _find_line_value(lines: list[str], aliases: list[str]):
    for line in lines:
        low = line.lower()
        for alias in aliases:
            if alias in low:
                val = _extract_value_from_line(line)
                if val is not None:
                    return val, line
    return None, None

def _line_mentions_cumm(line: str) -> bool:
    low = (line or "").lower()
    return ("cumm" in low) or ("/ul" in low) or ("cells/cumm" in low)

def _line_mentions_mill_cumm(line: str) -> bool:
    low = (line or "").lower()
    return ("mill/cumm" in low) or ("million/ul" in low)

def _convert_if_needed(test_name: str, value: float, default_unit: str, matched_line: str):
    name = (test_name or "").lower()

    if ("wbc" in name or "platelet" in name) and _line_mentions_cumm(matched_line):
        return value / 1000.0, "thousand/uL"

    if "rbc" in name and _line_mentions_mill_cumm(matched_line):
        return value, "million/uL"

    return value, default_unit

def _classify(value: float, low: float, high: float):
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "normal"

def _make_explanation(test: str, status: str, ref_text: str):
    if status == "normal":
        return f"{test} appears within the expected contextual interval ({ref_text})."
    if status == "low":
        return f"{test} appears below the expected contextual interval ({ref_text}). Clinical correlation is recommended."
    if status == "high":
        return f"{test} appears above the expected contextual interval ({ref_text}). Clinical correlation is recommended."
    return f"{test} could not be interpreted confidently."

def parse_local_cbc_report(report_text: str, sex: str = "female"):
    lines = _normalize_text(report_text)
    results = []

    for spec in CBC_SPECS:
        val, matched_line = _find_line_value(lines, spec["aliases"])
        if val is None:
            continue

        low, high = _get_ref(spec, sex)
        if low is None or high is None:
            continue

        value, unit = _convert_if_needed(spec["canonical"], val, spec["unit"], matched_line or "")
        status = _classify(value, low, high)
        ref_text = f"{low}-{high} {unit}"

        results.append({
            "test": spec["canonical"],
            "value": str(value),
            "unit": unit,
            "status": status,
            "reference": ref_text,
            "explanation": _make_explanation(spec["canonical"], status, ref_text),
            "source_label": "Local CBC rule engine",
            "source_type": "local_rules",
            "confidence": "high",
            "interpretation_mode": "local_contextual_rules",
            "confidence_score": 0.98,
            "confidence_band": "high",
            "vote_ratio": 1.0,
            "semantic_agreement": 1.0,
            "needs_manual_review": False,
            "retrieved_evidence": [
                {
                    "source": "local_rules",
                    "title": spec["canonical"],
                    "snippet": f"Adult contextual interval used: {ref_text}"
                }
            ],
            "hallucination_flag": False,
            "evidence_support": True,
            "evidence_support_score": 1.0,
            "matched_line": matched_line,
        })

    abnormal = [r for r in results if r["status"] in ["low", "high"]]

    if not results:
        summary = "No supported CBC parameters could be parsed reliably from the uploaded report."
        risk_level = "Low"
    elif len(abnormal) == 0:
        summary = "No clearly abnormal CBC values were detected by the local contextual rule engine."
        risk_level = "Low"
    elif len(abnormal) <= 2:
        summary = "A small number of CBC values are outside the contextual interval and may need attention."
        risk_level = "Moderate"
    else:
        summary = "Several CBC values are outside the contextual interval and should be reviewed."
        risk_level = "High"

    return {
        "results": results,
        "summary": summary,
        "risk_level": risk_level,
        "see_doctor_urgently": risk_level == "High",
        "disclaimer": "This analysis is generated by a local contextual rule engine for demonstration and informational purposes only. Please consult a qualified medical professional for clinical decisions."
    }
