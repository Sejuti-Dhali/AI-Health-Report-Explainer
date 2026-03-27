import json
import os
from groq import Groq

from models.schemas import AnalysisResponse, ReportParameter, RiskSummary, RangeStatus
from prompts.prompts import (
    PARSE_REPORT_PROMPT,
    CHAT_SYSTEM_PROMPT,
    TRANSLATE_BANGLA_PROMPT,
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


def parse_report_values(raw_text: str) -> AnalysisResponse:
    prompt = PARSE_REPORT_PROMPT.format(raw_text=raw_text)
    response_text = _call_llm(prompt, max_tokens=2048)

    clean = response_text.strip()

    # Extract fenced JSON block if present
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            if "{" in part and "}" in part:
                clean = part
                break

    # Remove optional leading 'json'
    clean = clean.replace("json", "").strip()

    # Extract the outermost JSON object
    start = clean.find("{")
    end = clean.rfind("}")
    if start != -1 and end != -1 and end > start:
        clean = clean[start:end + 1]

    try:
        data = json.loads(clean)
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
    composed = ""
    if report_context:
        composed += f"Report context:\n{report_context}\n\n"
    composed += f"User question:\n{question}"
    return _call_llm(composed, system_prompt=CHAT_SYSTEM_PROMPT, max_tokens=1024)


def translate_to_bangla(text: str) -> str:
    prompt = TRANSLATE_BANGLA_PROMPT.format(text=text)
    return _call_llm(prompt, max_tokens=2048)
