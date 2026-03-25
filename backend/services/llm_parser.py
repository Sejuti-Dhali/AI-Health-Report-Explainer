import os, json
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from groq import Groq
from backend.prompts.prompts import get_prompt, get_chat_prompt


def get_client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))


def analyze_report(report_text: str, language: str = "english") -> dict:
    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": get_prompt(report_text, language)},
            {"role": "user", "content": "Analyze this medical report and return JSON only."}
        ],
        temperature=0.1,
        max_tokens=2000,
    )
    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)


def answer_question(question: str, report_context: str, language: str = "english") -> dict:
    client = get_client()
    prompt = get_chat_prompt(question, report_context, language)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500,
    )
    answer = response.choices[0].message.content
    return {
        "answer": answer,
        "disclaimer": "⚠️ This is not medical advice. Please consult a qualified doctor."
    }