
"""
Standard reference ranges for common blood test parameters.
Used as a fallback reference — the LLM uses these implicitly via its training,
but this module can be used for rule-based validation if needed.
"""

REFERENCE_RANGES = {
    # Complete Blood Count (CBC)
    "hemoglobin": {"male": (13.5, 17.5), "female": (12.0, 15.5), "unit": "g/dL"},
    "hematocrit": {"male": (38.8, 50.0), "female": (34.9, 44.5), "unit": "%"},
    "rbc": {"male": (4.5, 5.9), "female": (4.1, 5.1), "unit": "million/uL"},
    "wbc": {"general": (4.5, 11.0), "unit": "thousand/uL"},
    "platelets": {"general": (150, 400), "unit": "thousand/uL"},
    "mcv": {"general": (80, 100), "unit": "fL"},
    "mch": {"general": (27, 33), "unit": "pg"},
    "mchc": {"general": (32, 36), "unit": "g/dL"},

    # Metabolic Panel
    "glucose_fasting": {"general": (70, 100), "unit": "mg/dL"},
    "glucose_random": {"general": (70, 140), "unit": "mg/dL"},
    "hba1c": {"general": (4.0, 5.6), "unit": "%"},
    "creatinine": {"male": (0.74, 1.35), "female": (0.59, 1.04), "unit": "mg/dL"},
    "bun": {"general": (7, 20), "unit": "mg/dL"},
    "sodium": {"general": (136, 145), "unit": "mEq/L"},
    "potassium": {"general": (3.5, 5.1), "unit": "mEq/L"},
    "calcium": {"general": (8.5, 10.2), "unit": "mg/dL"},

    # Lipid Panel
    "total_cholesterol": {"general": (0, 200), "unit": "mg/dL"},
    "ldl": {"general": (0, 100), "unit": "mg/dL"},
    "hdl": {"male": (40, 999), "female": (50, 999), "unit": "mg/dL"},
    "triglycerides": {"general": (0, 150), "unit": "mg/dL"},

    # Liver Function
    "alt": {"general": (7, 56), "unit": "U/L"},
    "ast": {"general": (10, 40), "unit": "U/L"},
    "bilirubin_total": {"general": (0.1, 1.2), "unit": "mg/dL"},
    "albumin": {"general": (3.5, 5.0), "unit": "g/dL"},

    # Thyroid
    "tsh": {"general": (0.4, 4.0), "unit": "mIU/L"},
    "t3": {"general": (100, 200), "unit": "ng/dL"},
    "t4": {"general": (5.0, 12.0), "unit": "ug/dL"},
}


def get_range(parameter_name: str, gender: str = "general"):
    """
    Return the reference range tuple for a given parameter.
    Falls back to 'general' if gender-specific not available.
    """
    key = parameter_name.lower().replace(" ", "_")
    entry = REFERENCE_RANGES.get(key)
    if not entry:
        return None
    range_tuple = entry.get(gender) or entry.get("general")
    return {"range": range_tuple, "unit": entry.get("unit")}

