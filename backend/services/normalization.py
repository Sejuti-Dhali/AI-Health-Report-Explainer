import re
from typing import Optional


ALIASES = {
    "hb": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "platelet count": "platelets",
    "platelets": "platelets",
    "rbc count": "rbc",
    "rbc": "rbc",
    "wbc count": "wbc",
    "wbc": "wbc",
    "packed cell volume": "hematocrit",
    "packed cell volume(pcv)": "hematocrit",
    "pcv": "hematocrit",
    "hematocrit": "hematocrit",
    "rbc indices - mcv": "mcv",
    "mcv": "mcv",
    "rbc indices - mch": "mch",
    "mch": "mch",
    "rbc indices - mchc": "mchc",
    "mchc": "mchc",
}


def normalize_parameter_name(name: str) -> str:
    if not name:
        return ""

    cleaned = name.strip().lower()
    cleaned = re.sub(r"[^a-z0-9\s\-_/()%]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if cleaned in ALIASES:
        return ALIASES[cleaned]

    return cleaned


def normalize_unit(unit: Optional[str]) -> str:
    if not unit:
        return ""

    unit = unit.strip()
    replacements = {
        "gm%": "g/dL",
        "gm/dl": "g/dL",
        "gms%": "g/dL",
        "/cumm": "/uL",
        "cells/cumm": "/uL",
        "mil/cumm": "million/uL",
        "lakhs/cumm": "100000/uL",
        "pgm": "pg",
    }

    key = unit.lower()
    return replacements.get(key, unit)


def normalize_value(value: str, unit: str, name: str = "") -> str:
    if value is None:
        return ""

    value = str(value).strip().replace(",", "")
    match = re.search(r"-?\d+(\.\d+)?", value)
    if not match:
        return value

    num = match.group(0)

    try:
        f = float(num)

        if unit == "g/dL" and "hemoglobin" in name and 30 < f < 300:
            return str(round(f / 10, 2))

        if unit == "g/dL" and "mchc" in name and 0 < f < 10:
            return str(round(f * 10, 2))

    except Exception:
        pass

    return num