import re

ANALYTE_SPECS = [
    # ---------- CBC ----------
    {
        "canonical": "Hemoglobin",
        "aliases": ["hemoglobin", "haemoglobin", "hb", "hgb"],
        "unit": "g/dL",
        "category": "CBC",
        "ref_male": (13.0, 17.0),
        "ref_female": (12.0, 15.0),
    },
    {
        "canonical": "RBC COUNT",
        "aliases": ["rbc count", "rbc", "red blood cell", "total rbc count"],
        "unit": "million/uL",
        "category": "CBC",
        "ref_male": (4.5, 5.9),
        "ref_female": (4.1, 5.1),
    },
    {
        "canonical": "Packed Cell Volume (PCV)",
        "aliases": ["packed cell volume", "pcv", "hematocrit", "hct"],
        "unit": "%",
        "category": "CBC",
        "ref_male": (40.0, 50.0),
        "ref_female": (36.0, 46.0),
    },
    {
        "canonical": "Mean Corpuscular Volume (MCV)",
        "aliases": ["mean corpuscular volume", "mcv"],
        "unit": "fL",
        "category": "CBC",
        "ref_general": (80.0, 100.0),
    },
    {
        "canonical": "MCH",
        "aliases": ["mch", "mean corpuscular hemoglobin"],
        "unit": "pg",
        "category": "CBC",
        "ref_general": (27.0, 33.0),
    },
    {
        "canonical": "MCHC",
        "aliases": ["mchc", "mean corpuscular hemoglobin concentration"],
        "unit": "g/dL",
        "category": "CBC",
        "ref_general": (32.0, 36.0),
    },
    {
        "canonical": "RDW",
        "aliases": ["rdw", "red cell distribution width"],
        "unit": "%",
        "category": "CBC",
        "ref_general": (11.5, 14.5),
    },
    {
        "canonical": "WBC COUNT",
        "aliases": ["wbc count", "wbc", "white blood cell", "total leukocyte count", "total wbc count"],
        "unit": "thousand/uL",
        "category": "CBC",
        "ref_general": (4.5, 11.0),
    },
    {
        "canonical": "Neutrophils",
        "aliases": ["neutrophils", "neutrophil"],
        "unit": "%",
        "category": "CBC",
        "ref_general": (40.0, 70.0),
    },
    {
        "canonical": "Lymphocytes",
        "aliases": ["lymphocytes", "lymphocyte"],
        "unit": "%",
        "category": "CBC",
        "ref_general": (20.0, 40.0),
    },
    {
        "canonical": "Eosinophils",
        "aliases": ["eosinophils", "eosinophil"],
        "unit": "%",
        "category": "CBC",
        "ref_general": (0.0, 6.0),
    },
    {
        "canonical": "Monocytes",
        "aliases": ["monocytes", "monocyte"],
        "unit": "%",
        "category": "CBC",
        "ref_general": (0.0, 10.0),
    },
    {
        "canonical": "Basophils",
        "aliases": ["basophils", "basophil"],
        "unit": "%",
        "category": "CBC",
        "ref_general": (0.0, 2.0),
    },
    {
        "canonical": "PLATELET COUNT",
        "aliases": ["platelet count", "platelet", "plt"],
        "unit": "thousand/uL",
        "category": "CBC",
        "ref_general": (150.0, 400.0),
    },

    # ---------- LIPID ----------
    {
        "canonical": "Total Cholesterol",
        "aliases": ["total cholesterol", "cholesterol total", "serum cholesterol"],
        "unit": "mg/dL",
        "category": "Lipid",
        "ref_general": (0.0, 200.0),
    },
    {
        "canonical": "LDL",
        "aliases": ["ldl cholesterol", "low density lipoprotein", "ldl"],
        "unit": "mg/dL",
        "category": "Lipid",
        "ref_general": (0.0, 100.0),
    },
    {
        "canonical": "HDL",
        "aliases": ["hdl cholesterol", "high density lipoprotein", "hdl"],
        "unit": "mg/dL",
        "category": "Lipid",
        "ref_general": (40.0, 100.0),
    },
    {
        "canonical": "Triglycerides",
        "aliases": ["triglycerides", "triglyceride", "tg"],
        "unit": "mg/dL",
        "category": "Lipid",
        "ref_general": (0.0, 150.0),
    },

    # ---------- LIVER ----------
    {
        "canonical": "ALT",
        "aliases": ["alanine aminotransferase", "sgpt", "alt"],
        "unit": "U/L",
        "category": "Liver",
        "ref_general": (7.0, 56.0),
    },
    {
        "canonical": "AST",
        "aliases": ["aspartate aminotransferase", "sgot", "ast"],
        "unit": "U/L",
        "category": "Liver",
        "ref_general": (10.0, 40.0),
    },
    {
        "canonical": "Bilirubin",
        "aliases": ["total bilirubin", "bilirubin"],
        "unit": "mg/dL",
        "category": "Liver",
        "ref_general": (0.1, 1.2),
    },
    {
        "canonical": "Albumin",
        "aliases": ["serum albumin", "albumin"],
        "unit": "g/dL",
        "category": "Liver",
        "ref_general": (3.5, 5.0),
    },

    # ---------- KIDNEY ----------
    {
        "canonical": "Creatinine",
        "aliases": ["serum creatinine", "creatinine"],
        "unit": "mg/dL",
        "category": "Kidney",
        "ref_male": (0.74, 1.35),
        "ref_female": (0.59, 1.04),
    },
    {
        "canonical": "BUN",
        "aliases": ["blood urea nitrogen", "urea nitrogen", "bun"],
        "unit": "mg/dL",
        "category": "Kidney",
        "ref_general": (7.0, 20.0),
    },
    {
        "canonical": "eGFR",
        "aliases": ["estimated gfr", "glomerular filtration rate", "egfr"],
        "unit": "mL/min/1.73m2",
        "category": "Kidney",
        "ref_general": (90.0, 1000.0),
    },

    # ---------- THYROID ----------
    {
        "canonical": "TSH",
        "aliases": ["thyroid stimulating hormone", "tsh"],
        "unit": "mIU/L",
        "category": "Thyroid",
        "ref_general": (0.4, 4.0),
    },
    {
        "canonical": "T3",
        "aliases": ["triiodothyronine", "t3"],
        "unit": "ng/dL",
        "category": "Thyroid",
        "ref_general": (80.0, 200.0),
    },
    {
        "canonical": "T4",
        "aliases": ["thyroxine", "t4"],
        "unit": "ug/dL",
        "category": "Thyroid",
        "ref_general": (5.0, 12.0),
    },

    # ---------- DIABETES ----------
    {
        "canonical": "HbA1c",
        "aliases": ["glycated hemoglobin", "hba1c", "a1c"],
        "unit": "%",
        "category": "Diabetes",
        "ref_general": (4.0, 5.6),
    },
    {
        "canonical": "Fasting Glucose",
        "aliases": ["fasting blood sugar", "glucose fasting", "fasting glucose", "fbs"],
        "unit": "mg/dL",
        "category": "Diabetes",
        "ref_general": (70.0, 99.0),
    },
]

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
        return spec["ref_male"]
    if sex != "male" and "ref_female" in spec:
        return spec["ref_female"]
    return spec.get("ref_general", spec.get("ref_female", spec.get("ref_male", (None, None))))

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
        # allow true analyte lines even if "female" or "male" appears somewhere else
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

def _calibrate_confidence(has_contextual_rule: bool, has_report_range: bool, hallucination_flag: bool):
    if hallucination_flag:
        return 0.40, "low"
    if has_contextual_rule:
        return 0.95, "high"
    if has_report_range:
        return 0.70, "moderate"
    return 0.40, "low"

def parse_local_cbc_report(report_text: str, sex: str = "female"):
    lines = _normalize_text(report_text)
    results = []

    for spec in ANALYTE_SPECS:
        raw_val, matched_line = _find_line_value(lines, spec["aliases"])
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

        confidence_score, confidence_band = _calibrate_confidence(
            has_contextual_rule=has_contextual_rule,
            has_report_range=(report_low is not None and report_high is not None),
            hallucination_flag=hallucination_flag
        )

        if hallucination_flag:
            explanation = f"{explanation} Warning: extraction/report consistency check found a mismatch ({hallucination_reason}). Manual review is recommended."

        results.append({
            "test": spec["canonical"],
            "category": spec["category"],
            "value": str(value),
            "unit": unit,
            "status": status,
            "reference": ref_text,
            "explanation": explanation,
            "source_label": "Extended local clinical rule engine",
            "source_type": "local_rules",
            "confidence": confidence_band,
            "interpretation_mode": "local_contextual_rules",
            "confidence_score": confidence_score,
            "confidence_band": confidence_band,
            "vote_ratio": 1.0 if not hallucination_flag else 0.5,
            "semantic_agreement": 1.0 if not hallucination_flag else 0.5,
            "needs_manual_review": bool(hallucination_flag),
            "retrieved_evidence": [
                {
                    "source": "local_rules",
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
        summary = "No clearly abnormal values were detected by the extended local rule engine."
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
        "disclaimer": "This analysis is generated by an extended local clinical rule engine for demonstration and informational purposes only. Please consult a qualified medical professional for clinical decisions."
    }
