import json
import os
from groq import Groq

from models.schemas import AnalysisResponse, ReportParameter, RiskSummary, RangeStatus
from prompts.prompts import (
    PARSE_REPORT_PROMPT,
    CHAT_SYSTEM_PROMPT,
    TRANSLATE_BANGLA_PROMPT,
)
from services.risk_engine import (
    compare_to_range,
    clinical_explanation,
    summarize_risk,
)

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


def _extract_json_text(response_text: str) -> str:
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

    return clean


def parse_report_values(raw_text: str) -> AnalysisResponse:
    prompt = PARSE_REPORT_PROMPT.format(raw_text=raw_text[:12000])
    response_text = _call_llm(prompt, max_tokens=2048)

    try:
        data = json.loads(_extract_json_text(response_text))
    except json.JSONDecodeError as e:
        print(f"[LLM] JSON parse error: {e}\nRaw: {response_text}")
        return AnalysisResponse(
            parameters=[],
            risk_summary=RiskSummary(
                level="Moderate",
                summary="The report text could not be parsed reliably. Please upload a clearer PDF or review the original report manually.",
                recommendations=[
                    "Try uploading a text-based PDF.",
                    "Review the original report with a clinician if findings are important.",
                ],
            ),
        )

    calibrated_parameters = []

    for p in data.get("parameters", []):
        name = p.get("name", "").strip()
        value = str(p.get("value", "")).strip()
        unit = p.get("unit") or ""
        llm_ref = p.get("reference_range") or ""

        rule_status, rule_ref = compare_to_range(name, value)
        final_status = rule_status if rule_status != "unknown" else p.get("status", "unknown")
        final_ref = llm_ref or rule_ref
        final_expl = clinical_explanation(name, final_status, value, final_ref)

        try:
            status_enum = RangeStatus(final_status)
        except Exception:
            status_enum = RangeStatus.UNKNOWN

        calibrated_parameters.append(
            ReportParameter(
                name=name,
                value=value,
                unit=unit,
                reference_range=final_ref,
                status=status_enum,
                explanation=final_expl,
            )
        )

    risk = summarize_risk(
        [
            {
                "name": p.name,
                "status": p.status.value,
                "value": p.value,
            }
            for p in calibrated_parameters
        ]
    )

    return AnalysisResponse(
        parameters=calibrated_parameters,
        risk_summary=RiskSummary(
            level=risk["level"],
            summary=risk["summary"],
            recommendations=risk["recommendations"],
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
