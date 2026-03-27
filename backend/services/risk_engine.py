import re
from typing import Optional, List, Dict, Any

from services.benchmark_loader import load_benchmarks, load_sources

BENCHMARKS = load_benchmarks()
SOURCES = load_sources()

ALIASES = {
    "hb": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "haemoglobin": "hemoglobin",

    "wbc": "wbc",
    "wbc count": "wbc",
    "total wbc count": "wbc",
    "white blood cells": "wbc",
    "white blood cell count": "wbc",

    "rbc": "rbc",
    "rbc count": "rbc",
    "red blood cells": "rbc",
    "red blood cell count": "rbc",

    "platelet count": "platelets",
    "platelets": "platelets",
    "plt": "platelets",

    "pcv": "pcv",
    "packed cell volume": "pcv",
    "hematocrit": "pcv",

    "mcv": "mcv",
    "mean corpuscular volume": "mcv",

    "mch": "mch",
    "mean corpuscular hemoglobin": "mch",

    "mchc": "mchc",
    "mean corpuscular hemoglobin concentration": "mchc",

    "rdw": "rdw",
    "rdw-cv": "rdw",

    "neutrophils": "neutrophils",
    "lymphocytes": "lymphocytes",
    "eosinophils": "eosinophils",
    "monocytes": "monocytes",
    "basophils": "basophils",

    "hba1c": "hba1c",
    "glycated hemoglobin": "hba1c",

    "fasting glucose": "glucose_fasting",
    "glucose fasting": "glucose_fasting",
    "fasting blood glucose": "glucose_fasting"
}


def normalize_name(name: str) -> str:
    key = name.strip().lower()
    return ALIASES.get(key, key.replace(" ", "_"))


def extract_numeric(value: str) -> Optional[float]:
    if value is None:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(match.group()) if match else None


def normalize_unit(unit: str) -> str:
    u = (unit or "").strip().lower()

    replacements = {
        "cumm": "/ul",
        "/cumm": "/ul",
        "cells/cumm": "/ul",
        "/cu mm": "/ul",
        "/mm3": "/ul",
        "/mm^3": "/ul",
        "cu mm": "/ul",
        "per ul": "/ul",
        "ul": "/ul",
        "10^9/l": "10^9/l",
        "x10^9/l": "10^9/l",
        "10^3/ul": "10^3/ul",
        "mil/cumm": "mil/cumm",
        "mill/cumm": "mil/cumm",
        "mill/mm3": "mil/cumm",
    }

    return replacements.get(u, u)


def convert_value_for_benchmark(numeric_value: float, report_unit: str, benchmark_unit: str) -> float:
    r_unit = normalize_unit(report_unit)
    b_unit = normalize_unit(benchmark_unit)

    if b_unit == "10^9/l" and r_unit == "/ul":
        return numeric_value / 1000.0

    return numeric_value


def get_benchmark_entry(name: str) -> Optional[Dict[str, Any]]:
    norm = normalize_name(name)
    return BENCHMARKS.get(norm)


def get_source_meta(source_id: Optional[str]) -> Dict[str, str]:
    if not source_id:
        return {"label": "Unknown source", "source_type": "unknown"}
    return SOURCES.get(source_id, {"label": source_id, "source_type": "unknown"})


def select_context(entry: Dict[str, Any], sex: str = "general", age_group: str = "adult"):
    contexts = entry.get("contexts", [])
    if not contexts:
        return None

    for ctx in contexts:
        if ctx.get("sex") == sex and ctx.get("age_group") == age_group:
            return ctx

    for ctx in contexts:
        if ctx.get("sex") == "general":
            return ctx

    return contexts[0]


def _unknown(mode: str) -> Dict[str, Any]:
    return {
        "status": "unknown",
        "reference": None,
        "source_label": "Unknown source",
        "source_type": "unknown",
        "confidence": "low",
        "interpretation_mode": mode,
    }


def evaluate_reference_interval(
    name: str,
    value: str,
    report_unit: str = "",
    sex: str = "general",
    age_group: str = "adult",
) -> Dict[str, Any]:
    entry = get_benchmark_entry(name)
    numeric = extract_numeric(value)

    if not entry or entry.get("kind") != "reference_interval":
        return _unknown("reference_interval")

    if numeric is None:
        return _unknown("reference_interval")

    ctx = select_context(entry, sex, age_group)
    if not ctx:
        return _unknown("reference_interval")

    low = ctx["low"]
    high = ctx["high"]
    benchmark_unit = entry.get("units_supported", [""])[0]

    normalized_value = convert_value_for_benchmark(
        numeric, report_unit, benchmark_unit
    )

    if normalized_value < low:
        status = "low"
    elif normalized_value > high:
        status = "high"
    else:
        status = "normal"

    source = get_source_meta(ctx.get("source_id"))

    return {
        "status": status,
        "reference": f"{low}-{high} {benchmark_unit}".strip(),
        "source_label": source["label"],
        "source_type": source["source_type"],
        "confidence": ctx.get("confidence", "medium"),
        "interpretation_mode": "reference_interval",
    }


def evaluate_decision_threshold(name: str, value: str) -> Dict[str, Any]:
    entry = get_benchmark_entry(name)
    numeric = extract_numeric(value)

    if not entry or entry.get("kind") != "decision_threshold":
        return _unknown("decision_threshold")

    if numeric is None:
        return _unknown("decision_threshold")

    thresholds = entry.get("thresholds", [])
    for th in thresholds:
        source = get_source_meta(th.get("source_id"))
        label = th.get("label", "unknown")
        operator = th.get("operator")

        if operator == "<" and numeric < th["value"]:
            return {
                "status": "normal" if label == "normal" else "high",
                "reference": f"{label}: < {th['value']}",
                "source_label": source["label"],
                "source_type": source["source_type"],
                "confidence": th.get("confidence", "medium"),
                "interpretation_mode": "decision_threshold",
            }

        if operator == "<=" and numeric <= th["value"]:
            return {
                "status": "normal" if label == "normal" else "high",
                "reference": f"{label}: <= {th['value']}",
                "source_label": source["label"],
                "source_type": source["source_type"],
                "confidence": th.get("confidence", "medium"),
                "interpretation_mode": "decision_threshold",
            }

        if operator == ">=" and numeric >= th["value"]:
            return {
                "status": "high",
                "reference": f"{label}: >= {th['value']}",
                "source_label": source["label"],
                "source_type": source["source_type"],
                "confidence": th.get("confidence", "medium"),
                "interpretation_mode": "decision_threshold",
            }

        if operator == "range" and th["low"] <= numeric <= th["high"]:
            return {
                "status": "high" if label != "normal" else "normal",
                "reference": f"{label}: {th['low']}-{th['high']}",
                "source_label": source["label"],
                "source_type": source["source_type"],
                "confidence": th.get("confidence", "medium"),
                "interpretation_mode": "decision_threshold",
            }

    if thresholds:
        source = get_source_meta(thresholds[0].get("source_id"))
        return {
            "status": "unknown",
            "reference": None,
            "source_label": source["label"],
            "source_type": source["source_type"],
            "confidence": "low",
            "interpretation_mode": "decision_threshold",
        }

    return _unknown("decision_threshold")


def evaluate_test(
    name: str,
    value: str,
    unit: str = "",
    sex: str = "general",
    age_group: str = "adult",
) -> Dict[str, Any]:
    entry = get_benchmark_entry(name)

    if not entry:
        return _unknown("unknown")

    if entry["kind"] == "reference_interval":
        return evaluate_reference_interval(name, value, unit, sex, age_group)

    if entry["kind"] == "decision_threshold":
        return evaluate_decision_threshold(name, value)

    return _unknown("unknown")


def clinical_explanation(
    name: str,
    status: str,
    reference: Optional[str],
    mode: str,
) -> str:
    if status == "normal":
        return f"{name} is within the expected range" + (f" ({reference})" if reference else "") + "."

    if status == "low":
        return f"{name} is below the expected range" + (f" ({reference})" if reference else "") + ". Clinical correlation is recommended."

    if status == "high":
        if mode == "decision_threshold":
            return f"{name} falls in a clinically relevant threshold category" + (f" ({reference})" if reference else "") + ". Clinical correlation is recommended."
        return f"{name} is above the expected range" + (f" ({reference})" if reference else "") + ". Clinical correlation is recommended."

    return f"{name} could not be confidently interpreted."


def summarize_risk(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    abnormal = sum(1 for p in parameters if p["status"] in ["high", "low"])

    if abnormal == 0:
        return {
            "level": "Low",
            "summary": "No abnormal values detected.",
            "recommendations": [
                "Review the full report with a clinician if symptoms are present."
            ],
        }

    if abnormal <= 2:
        return {
            "level": "Moderate",
            "summary": "Some values need attention.",
            "recommendations": [
                "Discuss the abnormal values with a qualified clinician.",
                "Interpret results together with symptoms and clinical history."
            ],
        }

    return {
        "level": "High",
        "summary": "Multiple abnormal values detected.",
        "recommendations": [
            "Seek medical review, especially if symptoms are present.",
            "Do not make treatment decisions based only on this AI summary."
        ],
    }
