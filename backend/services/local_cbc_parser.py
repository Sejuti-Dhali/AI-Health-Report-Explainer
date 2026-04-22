import re
from services.reference_loader import load_all_reference_specs

ANALYTE_SPECS = load_all_reference_specs()

NUMBER_RE = re.compile(r'(?<![A-Za-z])(\d+(?:\.\d+)?)')

ADDRESS_WORDS = {
    "road", "rd", "street", "st", "avenue", "ave", "complex", "opposite", "mumbai",
    "bangalore", "dhaka", "khulna", "india", "bangladesh", "bypass", "floor", "plot",
    "house", "bungalow", "tower", "sector", "block", "near", "opp", "address", "pin", "phone"
}

HEADER_NOISE_WORDS = {
    "age", "years", "gender", "female", "male", "patient", "name", "doctor", "sample",
    "collected", "reported", "laboratory", "lab no", "bill no", "ref by", "smart vision"
}

UNIT_HINTS = [
    "mg/dl", "g/dl", "u/l", "miu/l", "ng/dl", "ug/dl", "fl", "pg", "%", "cumm",
    "million", "thousand", "ml/min", "mmol/l"
]

def _normalize_text(text: str) -> list[str]:
    text = text.replace("\r", "\n")
    lines = [ln.strip() for ln in text.split("\n")]
    return [ln for ln in lines if ln]

def _get_ref(spec: dict, sex: str):
    sex = (sex or "female").strip().lower()
    if sex == "male" and "ref_male" in spec:
        return tuple(spec["ref_male"])
    if sex != "male" and "ref_female" in spec:
        return tuple(spec["ref_female"])
    if "ref_general" in spec:
        return tuple(spec["ref_general"])
    return (None, None)

def _extract_all_numbers(line: str):
    nums = NUMBER_RE.findall(line or "")
    out = []
    for x in nums:
        try:
            out.append(float(x))
        except Exception:
            pass
    return out

def _extract_value_from_line(line: str):
    nums = _extract_all_numbers(line)
    if not nums:
        return None
    return nums[0]

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

def _classify(value: float, low: float, high: float, analyte: str = ""):
    name = (analyte or "").lower()

    if "egfr" in name:
        if value < low:
            return "low"
        return "normal"

    if name == "hdl":
        if value < low:
            return "low"
        return "normal"

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

def _extract_report_reference(line: str):
    nums = _extract_all_numbers(line)
    if len(nums) >= 3:
        return nums[1], nums[2]
    return None, None

def _extract_report_flag_keyword(line: str):
    low = (line or "").lower()
    if " low " in f" {low} ":
        return "low"
    if " high " in f" {low} ":
        return "high"
    if " normal " in f" {low} ":
        return "normal"
    if " borderline " in f" {low} ":
        return "borderline"
    return None

def _is_noise_line(line: str) -> bool:
    low = (line or "").lower()
    if any(word in low for word in ADDRESS_WORDS):
        return True
    if any(word in low for word in HEADER_NOISE_WORDS):
        if not any(h in low for h in UNIT_HINTS):
            return True
    return False

def _has_lab_shape(line: str) -> bool:
    low = (line or "").lower()
    nums = _extract_all_numbers(line)
    if len(nums) == 0:
        return False
    if any(h in low for h in UNIT_HINTS):
        return True
    if len(nums) >= 2:
        return True
    if " low " in f" {low} " or " high " in f" {low} " or " borderline " in f" {low} ":
        return True
    return False

def _alias_value_close(line: str, alias: str) -> bool:
    low = (line or "").lower()
    idx = low.find(alias)
    if idx == -1:
        return False

    tail = low[idx: idx + 60]
    nums = NUMBER_RE.findall(tail)
    if nums:
        return True

    head = low[max(0, idx - 20): idx + len(alias)]
    nums2 = NUMBER_RE.findall(head)
    return bool(nums2)

def _find_line_value(lines: list[str], aliases: list[str]):
    for line in lines:
        if _is_noise_line(line):
            continue
        if not _has_lab_shape(line):
            continue

        low = line.lower()
        for alias in aliases:
            if alias in low and _alias_value_close(line, alias):
                val = _extract_value_from_line(line)
                if val is not None:
                    return val, line
    return None, None

def _hallucination_proxy(raw_value, report_low, report_high, report_flag_keyword, analyte_name=""):
    if raw_value is None:
        return True, 0.2, "no_value_extracted"

    if report_low is not None and report_high is not None:
        computed_status = _classify(raw_value, report_low, report_high, analyte=analyte_name)
        if report_flag_keyword in ["low", "high", "normal"] and computed_status != report_flag_keyword:
            return True, 0.2, f"report_flag_mismatch:{report_flag_keyword}_vs_{computed_status}"
        return False, 1.0, "value_and_report_range_consistent"

    return False, 0.75, "value_present_but_report_range_missing"

def _calibrate_confidence(source_tier: str, has_contextual_rule: bool, has_report_range: bool, hallucination_flag: bool):
    if hallucination_flag:
        return 0.40, "low"
    if source_tier == "primary_guideline" and has_contextual_rule:
        return 0.95, "high"
    if has_contextual_rule:
        return 0.85, "high"
    if has_report_range:
        return 0.70, "moderate"
    return 0.40, "low"

def parse_local_lab_report(report_text: str, sex: str = "female"):
    lines = _normalize_text(report_text)
    results = []

    for spec in ANALYTE_SPECS:
        raw_val, matched_line = _find_line_value(lines, spec.get("aliases", []))
        if raw_val is None:
            continue

        low, high = _get_ref(spec, sex)
        has_contextual_rule = low is not None and high is not None

        report_low, report_high = _extract_report_reference(matched_line or "")
        report_flag_keyword = _extract_report_flag_keyword(matched_line or "")

        hallucination_flag, evidence_support_score, hallucination_reason = _hallucination_proxy(
            raw_value=raw_val,
            report_low=report_low,
            report_high=report_high,
            report_flag_keyword=report_flag_keyword,
            analyte_name=spec["canonical"]
        )

        value, unit = _convert_if_needed(spec["canonical"], raw_val, spec["unit"], matched_line or "")

        if has_contextual_rule:
            status = _classify(value, low, high, analyte=spec["canonical"])
            ref_text = f"{low}-{high} {unit}"
            explanation = _make_explanation(spec["canonical"], status, ref_text)
        elif report_low is not None and report_high is not None:
            status = _classify(raw_val, report_low, report_high, analyte=spec["canonical"])
            ref_text = f"{report_low}-{report_high} reported"
            explanation = f"{spec['canonical']} was interpreted using the report-provided reference range ({ref_text})."
        else:
            status = "unknown"
            ref_text = "unknown"
            explanation = f"{spec['canonical']} could not be interpreted confidently."

        source_tier = spec.get("source_tier", "starter_local_reference_needs_validation")
        confidence_score, confidence_band = _calibrate_confidence(
            source_tier=source_tier,
            has_contextual_rule=has_contextual_rule,
            has_report_range=(report_low is not None and report_high is not None),
            hallucination_flag=hallucination_flag
        )

        if hallucination_flag:
            explanation = f"{explanation} Warning: extraction/report consistency check found a mismatch ({hallucination_reason}). Manual review is recommended."

        results.append({
            "test": spec["canonical"],
            "category": spec.get("category", "General"),
            "value": str(value),
            "unit": unit,
            "status": status,
            "reference": ref_text,
            "explanation": explanation,
            "source_label": spec.get("source_label", "Reference loader"),
            "source_type": "json_reference_rules",
            "source_tier": source_tier,
            "source_citation": spec.get("source_citation"),
            "confidence": confidence_band,
            "interpretation_mode": "panel_driven_local_rules",
            "confidence_score": confidence_score,
            "confidence_band": confidence_band,
            "vote_ratio": 1.0 if not hallucination_flag else 0.5,
            "semantic_agreement": 1.0 if not hallucination_flag else 0.5,
            "needs_manual_review": bool(hallucination_flag),
            "retrieved_evidence": [
                {
                    "source": "reference_json",
                    "title": spec["canonical"],
                    "snippet": f"Contextual interval used: {ref_text}"
                }
            ],
            "hallucination_flag": hallucination_flag,
            "hallucination_reason": hallucination_reason,
            "evidence_support": not hallucination_flag,
            "evidence_support_score": evidence_support_score,
            "matched_line": matched_line,
            "report_reference_low": report_low,
            "report_reference_high": report_high,
            "report_flag_keyword": report_flag_keyword,
        })

    abnormal = [r for r in results if r["status"] in ["low", "high"]]

    if not results:
        summary = "No supported lab parameters could be parsed reliably from the uploaded report."
        risk_level = "Low"
    elif len(abnormal) == 0:
        summary = "No clearly abnormal values were detected by the panel-driven local rule engine."
        risk_level = "Low"
    elif len(abnormal) <= 2:
        summary = "A small number of values are outside the contextual interval and may need attention."
        risk_level = "Moderate"
    else:
        summary = "Several values are outside the contextual interval and should be reviewed."
        risk_level = "High"

    return {
        "results": results,
        "summary": summary,
        "risk_level": risk_level,
        "see_doctor_urgently": risk_level == "High",
        "disclaimer": "This analysis is generated by a panel-driven local clinical rule engine for demonstration and informational purposes only. Please consult a qualified medical professional for clinical decisions."
    }

# backwards compatibility for current route import
def parse_local_cbc_report(report_text: str, sex: str = "female"):
    return parse_local_lab_report(report_text, sex=sex)
