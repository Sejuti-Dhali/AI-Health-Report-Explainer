def get_conditioned_range(test_name, value, unit, age=None, sex=None, bmi=None, condition=None):
    try:
        v = float(value)
    except Exception:
        return {
            "conditioned_range": "unknown",
            "status": "unknown",
            "personalized_explanation": "Value could not be interpreted."
        }

    test = (test_name or "").lower()
    sex_norm = (sex or "female").strip().lower()
    age_text = age if age is not None else "unknown"
    condition_text = condition if condition else "none"

    if "hemo" in test:
        if sex_norm == "male":
            low, high = 13.0, 17.0
        else:
            low, high = 12.0, 15.0

        if v < low:
            status = "low"
        elif v > high:
            status = "high"
        else:
            status = "normal"

        return {
            "conditioned_range": f"{low}-{high} g/dL",
            "status": status,
            "personalized_explanation": f"For a {age_text}-year-old {sex_norm} with condition '{condition_text}', this hemoglobin is {status} relative to the contextual range."
        }

    if "wbc" in test or "white blood" in test or "leukocyte" in test:
        val = v
        low, high = 4.5, 11.0
        if val < low:
            status = "low"
        elif val > high:
            status = "high"
        else:
            status = "normal"

        return {
            "conditioned_range": f"{low}-{high} thousand/uL",
            "status": status,
            "personalized_explanation": f"For a {age_text}-year-old {sex_norm} with condition '{condition_text}', this white blood cell count is {status} relative to the contextual interval."
        }

    if "platelet" in test or "plt" in test:
        val = v
        low, high = 150.0, 400.0
        if val < low:
            status = "low"
        elif val > high:
            status = "high"
        else:
            status = "normal"

        return {
            "conditioned_range": f"{int(low)}-{int(high)} thousand/uL",
            "status": status,
            "personalized_explanation": f"For a {age_text}-year-old {sex_norm} with condition '{condition_text}', this platelet count is {status} relative to the contextual interval."
        }

    return {
        "conditioned_range": "unknown",
        "status": "unknown",
        "personalized_explanation": "No personalized logic available for this test yet."
    }
