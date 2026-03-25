import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from groq import Groq
from prompts.prompts import get_prompt

client = Groq(api_key=os.environ["GROQ_API_KEY"])

test_report = """
Patient: Female, 32 years
HbA1c: 7.2%
Hemoglobin: 10.1 g/dL
TSH: 6.8 mIU/L
Total Cholesterol: 215 mg/dL
"""

response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[
        {"role": "system", "content": get_prompt(test_report)},
        {"role": "user", "content": "Analyze this report."}
    ],
    temperature=0.1,
    max_tokens=2000,
)

result = json.loads(response.choices[0].message.content)

print("=== RESULTS ===")
for r in result["results"]:
    print(f"{r['test']}: {r['value']} {r['unit']} → {r['status']}")

print(f"\nUrgent: {result['see_doctor_urgently']}")
print(f"Summary: {result['summary']}")
