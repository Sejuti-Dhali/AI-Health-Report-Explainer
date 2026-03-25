REFERENCE_RANGES = {
    "Hemoglobin": {
        "male":   {"low": 13.5, "high": 17.5, "unit": "g/dL"},
        "female": {"low": 12.0, "high": 15.5, "unit": "g/dL"},
    },
    "WBC": {"low": 4.0, "high": 11.0, "unit": "×10³/µL"},
    "Platelets": {"low": 150, "high": 400, "unit": "×10³/µL"},
    "Blood Glucose (Fasting)": {
        "normal_max": 99, "prediabetes_max": 125, "unit": "mg/dL"
    },
    "HbA1c": {
        "normal_max": 5.6, "prediabetes_max": 6.4, "unit": "%"
    },
    "Total Cholesterol": {
        "normal_max": 200, "borderline_max": 239, "unit": "mg/dL"
    },
    "LDL": {"normal_max": 100, "unit": "mg/dL"},
    "HDL": {"male_min": 40, "female_min": 50, "unit": "mg/dL"},
    "Triglycerides": {
        "normal_max": 150, "borderline_max": 199, "unit": "mg/dL"
    },
    "Creatinine": {
        "male":   {"low": 0.74, "high": 1.35, "unit": "mg/dL"},
        "female": {"low": 0.59, "high": 1.04, "unit": "mg/dL"},
    },
    "TSH": {"low": 0.4, "high": 4.0, "unit": "mIU/L"},
    "ALT": {"normal_max": 40, "unit": "U/L"},
    "AST": {"normal_max": 40, "unit": "U/L"},
    "Bilirubin (Total)": {"normal_max": 1.2, "unit": "mg/dL"},
    "Uric Acid": {
        "male":   {"normal_max": 7.0, "unit": "mg/dL"},
        "female": {"normal_max": 6.0, "unit": "mg/dL"},
    },
    "Sodium": {"low": 136, "high": 145, "unit": "mEq/L"},
    "Potassium": {"low": 3.5, "high": 5.1, "unit": "mEq/L"},
    "Calcium": {"low": 8.5, "high": 10.5, "unit": "mg/dL"},
}


def get_range_context() -> str:
    lines = []
    for test, ranges in REFERENCE_RANGES.items():
        lines.append(f"- {test}: {ranges}")
    return "\n".join(lines)