import json
import os
import re
from groq import Groq

from models.schemas import AnalysisResponse, ReportParameter, RiskSummary, RangeStatus
from prompts.prompts import (
    PARSE_REPORT_PROMPT,
    CHAT_SYSTEM_PROMPT,
    TRANSLATE_BANGLA_PROMPT,
)
from prompts.reference_ranges import get_range
from services.normalization import (
    normalize_parameter_name,
    normalize_unit,
    normalize_value,
)
from services.reference_ranges import REFERENCE_RANGES

MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


def _get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Add it to backend/.env and restart the server.")
    return Groq(api_key=api_key)


def _call_llm(user_prompt: str, system_prompt: str = None, max_tokens: int = 2048) -> str:
    client = _get_client()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


def _extract_json_object(response_text: str) -> dict:
    clean = response_text.strip()

    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            if "{" in part and "}" in part:
                clean = part
                break

    clean = clean.replace("json", "").strip()

    start = clean.find("{")
    end = clean.rfind("}")
    if start != -1 and end != -1 and end > start:
        clean = clean[start:end + 1]

    return json.loads(clean)


def _try_float(value: str):
    if value is None:
        return None

    match = re.search(r"-?\d+(\.\d+)?", str(value).replace(",", ""))
    if not match:
        return None

    try:
        return float(match.group(0))
    except Exception:
        return None


def _should_keep_parameter(name: str, value: str, unit: str, report_reference: str) -> bool:
    if not name or len(name.strip()) < 2:
        return False

    numeric_value = _try_float(value)
    if numeric_value is None:
        return False

    if unit or report_reference:
        return True

    common_terms = [
        "hemoglobin", "hb", "wbc", "rbc", "platelet", "platelets",
        "mcv", "mch", "mchc", "pcv", "hematocrit", "glucose",
        "creatinine", "urea", "sodium", "potassium", "tsh",
        "cholesterol", "hdl", "ldl", "triglycerides",
    ]
    lowered = name.lower()
    return any(term in lowered for term in common_terms)


def _get_reference_source(name: str) -> str | None:
    lowered = (name or "").lower()
    lowered = lowered.replace("_", " ").replace("-", " ").strip()

    for _, spec in REFERENCE_RANGES.items():
        aliases = spec.get("aliases", [])
        if any(alias in lowered for alias in aliases):
            return spec.get("source")

    return None


def _evaluate_test(name: str, value: str, unit: str = "", report_reference: str = ""):
    """
    Conservative rule-based evaluation.
    Uses local reference ranges when available.
    Falls back to report-provided reference if local reference not found.
    """
    parsed_value = _try_float(value)
    if parsed_value is None:
        return {
            "status": "unknown",
            "reference": report_reference,
            "interpretation_mode": "unknown",
            "source": None,
        }

    ref = get_range(name)

    if not ref and name == "hemoglobin":
        ref = get_range("hemoglobin")

    if not ref and name == "platelets":
        ref = get_range("platelets")

    if not ref and "rbc count" in name:
        ref = get_range("rbc")

    if not ref and name == "wbc":
        ref = get_range("wbc")

    if not ref and "packed cell volume" in name:
        ref = get_range("hematocrit")

    source = _get_reference_source(name)

    if ref and ref.get("range"):
        low, high = ref["range"]
        ref_unit = ref.get("unit", "")

        adjusted_value = parsed_value

        # /uL vs thousand/uL
        if unit == "/uL" and ref_unit == "thousand/uL":
            adjusted_value = parsed_value / 1000.0

        reference_text = f"{low}-{high} {ref_unit}".strip()

        if adjusted_value < low:
            return {
                "status": "low",
                "reference": reference_text,
                "interpretation_mode": "reference_interval",
                "source": source,
            }
        if adjusted_value > high:
            return {
                "status": "high",
                "reference": reference_text,
                "interpretation_mode": "reference_interval",
                "source": source,
            }
        return {
            "status": "normal",
            "reference": reference_text,
            "interpretation_mode": "reference_interval",
            "source": source,
        }

    return {
        "status": "unknown",
        "reference": report_reference,
        "interpretation_mode": "unknown",
        "source": None,
    }


def _clinical_explanation(display_name: str, status: str, reference_text: str, mode: str) -> str:
    name = display_name or "This parameter"

    if status == "normal":
        if reference_text:
            return f"{name} appears to be within the expected range ({reference_text})."
        return f"{name} appears to be within the expected range."

    if status == "low":
        if reference_text:
            return f"{name} is below the expected range ({reference_text}). Clinical correlation is recommended."
        return f"{name} appears lower than expected. Clinical correlation is recommended."

    if status == "high":
        if reference_text:
            return f"{name} is above the expected range ({reference_text}). Clinical correlation is recommended."
        return f"{name} appears higher than expected. Clinical correlation is recommended."

    if mode == "unknown":
        return f"{name} could not be confidently interpreted."

    return f"{name} needs further review."


def parse_report_values(raw_text: str) -> AnalysisResponse:
    prompt = PARSE_REPORT_PROMPT.format(raw_text=raw_text)
    response_text = _call_llm(prompt, max_tokens=2048)

    try:
        data = _extract_json_object(response_text)
    except json.JSONDecodeError as e:
        print(f"[LLM] JSON parse error: {e}\nRaw: {response_text}")
        return AnalysisResponse(
            parameters=[],
            risk_summary=RiskSummary(
                level="Unknown",
                summary="Could not parse the report. Please try again.",
                recommendations=[],
            ),
        )

    calibrated_parameters = []

    for p in data.get("parameters", []):
        raw_name = p.get("name", "").strip()
        raw_value = str(p.get("value", "")).strip()
        raw_unit = (p.get("unit") or "").strip()
        report_reference = (p.get("reference_range") or "").strip()

        name = normalize_parameter_name(raw_name)
        unit = normalize_unit(raw_unit)
        value = normalize_value(raw_value, unit, name)

        if not _should_keep_parameter(raw_name, value, unit, report_reference):
            continue

        benchmark = _evaluate_test(
            name,
            value,
            unit=unit,
            report_reference=report_reference,
        )

        final_status = benchmark["status"]
        final_reference = benchmark["reference"] or report_reference
        final_source = benchmark.get("source")
        final_explanation = _clinical_explanation(
            raw_name,
            final_status,
            final_reference,
            benchmark["interpretation_mode"],
        )

        try:
            status_enum = RangeStatus(final_status)
        except Exception:
            status_enum = RangeStatus.UNKNOWN

        calibrated_parameters.append(
            ReportParameter(
                name=raw_name,
                value=value,
                unit=unit,
                reference_range=final_reference,
                status=status_enum,
                explanation=final_explanation,
                source=final_source,
            )
        )

    llm_rs = data.get("risk_summary", {}) or {}
    llm_level = llm_rs.get("level", "Unknown")
    llm_summary = llm_rs.get("summary", "").strip()
    llm_recommendations = llm_rs.get("recommendations", [])

    high_count = sum(1 for p in calibrated_parameters if p.status == RangeStatus.HIGH)
    low_count = sum(1 for p in calibrated_parameters if p.status == RangeStatus.LOW)
    abnormal_count = high_count + low_count

    if abnormal_count >= 3:
        level = "High"
    elif abnormal_count >= 1:
        level = "Moderate"
    elif calibrated_parameters:
        level = "Low"
    else:
        level = llm_level if llm_level else "Unknown"

    if calibrated_parameters:
        if abnormal_count == 0:
            summary = "Most clearly interpretable values appear within expected ranges."
        elif abnormal_count == 1:
            summary = "One clearly interpretable value appears outside the expected range and may need attention."
        else:
            summary = "Some clearly interpretable values are outside the expected range and may need attention."
    else:
        summary = llm_summary or "Could not confidently interpret the report."

    recommendations = llm_recommendations if isinstance(llm_recommendations, list) else []
    if not recommendations:
        recommendations = [
            "Review these results with a qualified medical professional.",
            "Use the original report for final clinical interpretation.",
        ]

    return AnalysisResponse(
        parameters=calibrated_parameters,
        risk_summary=RiskSummary(
            level=level,
            summary=summary,
            recommendations=recommendations,
        ),
    )


def answer_followup_question(question: str, report_context: str = "") -> str:
    composed = ""
    if report_context:
        composed += f"Report context:\n{report_context}\n\n"
    composed += f"User question:\n{question}"
    return _call_llm(composed, system_prompt=CHAT_SYSTEM_PROMPT, max_tokens=1024)


def translate_to_bangla(text: str) -> str:
    prompt = TRANSLATE_BANGLA_PROMPT.format(text=text)
    return _call_llm(prompt, max_tokens=2048)