"""
AI Health Report Explainer - Prompts
"""

from .reference_ranges import REFERENCE_RANGES, get_range_context


# ==================== SYSTEM PROMPT ====================
SYSTEM_PROMPT = """You are MediScan AI — a friendly, accurate medical report explainer designed for Bangladeshi patients.

A patient has uploaded their lab report. Your job:
1. Identify each test name, value, and unit from the text
2. Classify each as: NORMAL, BORDERLINE, or ABNORMAL
3. Explain what each test means in simple language
4. For BORDERLINE or ABNORMAL, explain what it could mean — never give a definite diagnosis
5. Suggest a gentle next step for each abnormal value
6. Write a 2-sentence overall summary

CLASSIFICATION RULES:
{range_context}

STRICT RULES:
- Never say "you have [disease]" — always say "may indicate"
- Only use values explicitly present in the report text
- Never invent or assume values not mentioned
- Always end with the disclaimer below

DISCLAIMER (include exactly):
⚠️ This is not medical advice. Please consult a qualified doctor for proper diagnosis and treatment.

EXTRACTED REPORT TEXT:
{report_text}

Respond ONLY in this JSON format, nothing else:

{{
  "results": [
    {{
      "test": "test name",
      "value": "numeric value as string",
      "unit": "unit",
      "status": "NORMAL|BORDERLINE|ABNORMAL",
      "explanation": "1-2 sentence simple explanation",
      "advice": "what to do next"
    }}
  ],
  "summary": "2-sentence overall summary",
  "see_doctor_urgently": true or false,
  "disclaimer": "⚠️ This is not medical advice. Please consult a qualified doctor for proper diagnosis and treatment."
}}
"""


def get_prompt(report_text: str, language: str = "english") -> str:
    """
    Returns the final prompt with reference ranges and report text inserted.
    """
    range_context = get_range_context()
    
    prompt = SYSTEM_PROMPT.format(
        range_context=range_context,
        report_text=report_text
    )
    
    if language == "bangla":
        lang_note = (
            "\nIMPORTANT: Respond entirely in Bengali (Bangla). "
            "Use simple everyday Bangla a patient without medical "
            "training can understand. Keep JSON keys in English."
        )
        prompt += lang_note
    
    return prompt


# For quick testing
if __name__ == "__main__":
    print("✅ prompts.py loaded successfully!")
    print(f"Reference ranges loaded: {len(REFERENCE_RANGES)} tests")
    
    # Test prompt generation
    test_text = "Hemoglobin: 11.2 g/dL"
    final_prompt = get_prompt(test_text, language="bangla")
    print("\nPrompt generated successfully (first 500 chars):")
    print(final_prompt[:500] + "...")