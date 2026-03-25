import json
import os
import anthropic

from models.schemas import AnalysisResponse, ReportParameter, RiskSummary, RangeStatus
from prompts.prompts import (
    PARSE_REPORT_PROMPT,
    CHAT_SYSTEM_PROMPT,
    TRANSLATE_BANGLA_PROMPT,
)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-opus-4-5"


def parse_report_values(raw_text: str) -> AnalysisResponse:
    """
    Send OCR text to Claude → get structured JSON → return AnalysisResponse.
    """
    prompt = PARSE_REPORT_PROMPT.format(raw_text=raw_text)

    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text

    # Strip markdown fences if present
    clean = response_text.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip().rstrip("```").strip()

    try:
        data = json.loads(clean)
    except json.JSONDecodeError as e:
        print(f"[LLM] JSON parse error: {e}\nRaw: {response_text}")
        # Return a safe fallback
        return AnalysisResponse(
            parameters=[],
            risk_summary=RiskSummary(
                level="Unknown",
                summary="Could not parse the report. Please try again.",
                recommendations=[],
            ),
        )

    parameters = [
        ReportParameter(
            name=p.get("name", ""),
            value=str(p.get("value", "")),
            unit=p.get("unit"),
            reference_range=p.get("reference_range"),
            status=RangeStatus(p.get("status", "unknown")),
            explanation=p.get("explanation"),
        )
        for p in data.get("parameters", [])
    ]

    rs = data.get("risk_summary", {})
    risk_summary = RiskSummary(
        level=rs.get("level", "Unknown"),
        summary=rs.get("summary", ""),
        recommendations=rs.get("recommendations", []),
    )

    return AnalysisResponse(parameters=parameters, risk_summary=risk_summary)


def answer_followup_question(question: str, report_context: str = "") -> str:
    """
    Answer a user's follow-up question in plain language.
    """
    messages = []
    if report_context:
        messages.append({"role": "user", "content": f"Report context:\n{report_context}"})
        messages.append({"role": "assistant", "content": "Understood. I have the report context."})
    messages.append({"role": "user", "content": question})

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=CHAT_SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def translate_to_bangla(text: str) -> str:
    """
    Translate the given text to Bangla using Claude.
    """
    prompt = TRANSLATE_BANGLA_PROMPT.format(text=text)
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text