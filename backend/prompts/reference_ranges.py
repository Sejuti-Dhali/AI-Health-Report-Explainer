REFERENCE_RANGES = {

    # ── CBC (Complete Blood Count) ──────────────────────────
    "Hemoglobin": {
        "male":   {"low": 13.5, "high": 17.5},
        "female": {"low": 12.0, "high": 15.5},
        "unit": "g/dL",
        "borderline_gap": 1.0
    },
    "WBC": {
        "low": 4.0, "high": 11.0,
        "unit": "×10³/µL"
    },
    "Platelets": {
        "low": 150, "high": 400,
        "unit": "×10³/µL"
    },
    "RBC": {
        "male":   {"low": 4.5, "high": 5.9},
        "female": {"low": 4.0, "high": 5.2},
        "unit": "×10⁶/µL"
    },

    # ── Blood Sugar ─────────────────────────────────────────
    "Blood Glucose (Fasting)": {
        "normal_max": 99,
        "prediabetes_max": 125,
        "unit": "mg/dL",
        "flag": {
            "normal":     "Blood sugar is within healthy range.",
            "prediabetes":"Slightly elevated. Lifestyle changes recommended.",
            "high":       "May indicate diabetes risk. Consult a doctor."
        }
    },
    "Blood Glucose (Random)": {
        "normal_max": 139,
        "prediabetes_max": 199,
        "unit": "mg/dL"
    },
    "HbA1c": {
        "normal_max": 5.6,
        "prediabetes_max": 6.4,
        "unit": "%",
        "flag": {
            "normal":     "Good long-term blood sugar control.",
            "prediabetes":"Indicates prediabetes risk.",
            "high":       "Indicates possible diabetes. Please see a doctor."
        }
    },

    # ── Lipid Panel ─────────────────────────────────────────
    "Total Cholesterol": {
        "normal_max": 199,
        "borderline_max": 239,
        "unit": "mg/dL"
    },
    "LDL Cholesterol": {
        "optimal_max": 99,
        "normal_max": 129,
        "borderline_max": 159,
        "unit": "mg/dL"
    },
    "HDL Cholesterol": {
        "male_low": 40,
        "female_low": 50,
        "unit": "mg/dL",
        "note": "Higher is better for HDL"
    },
    "Triglycerides": {
        "normal_max": 149,
        "borderline_max": 199,
        "unit": "mg/dL"
    },

    # ── Kidney Function ─────────────────────────────────────
    "Creatinine": {
        "male":   {"low": 0.74, "high": 1.35},
        "female": {"low": 0.59, "high": 1.04},
        "unit": "mg/dL"
    },
    "BUN": {
        "low": 7, "high": 20,
        "unit": "mg/dL"
    },
    "Uric Acid": {
        "male":   {"high": 7.0},
        "female": {"high": 6.0},
        "unit": "mg/dL"
    },

    # ── Liver Function ──────────────────────────────────────
    "ALT": {
        "male":   {"high": 40},
        "female": {"high": 31},
        "unit": "U/L"
    },
    "AST": {
        "high": 40,
        "unit": "U/L"
    },
    "Bilirubin (Total)": {
        "high": 1.2,
        "unit": "mg/dL"
    },

    # ── Thyroid ─────────────────────────────────────────────
    "TSH": {
        "low": 0.4, "high": 4.0,
        "unit": "mIU/L",
        "flag": {
            "low":  "May indicate hyperthyroidism (overactive thyroid).",
            "high": "May indicate hypothyroidism (underactive thyroid)."
        }
    },
    "T3": {
        "low": 80, "high": 200,
        "unit": "ng/dL"
    },
    "T4": {
        "low": 5.1, "high": 14.1,
        "unit": "µg/dL"
    },
}
def get_range_context() -> str:
    """
    Returns a plain-text summary of all reference ranges.
    This gets injected into the LLM system prompt.
    """
    lines = ["REFERENCE RANGES FOR CLASSIFICATION:\n"]
    for test, data in REFERENCE_RANGES.items():
        unit = data.get("unit", "")
        lines.append(f"- {test} ({unit}): {data}")
    return "\n".join(lines)
