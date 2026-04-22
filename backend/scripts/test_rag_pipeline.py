from services.rag.rag_pipeline import single_call_rag, run_rag_pipeline

def dummy_llm(prompt):
    return """{
        "status": "low",
        "explanation": "Hemoglobin appears below the retrieved reference interval. Clinical correlation is recommended.",
        "evidence_used": ["pubmed", "loinc"]
    }"""

patient_result = {
    "test": "Hemoglobin",
    "value": "12.5",
    "unit": "g/dL",
    "reference": "13.0 - 17.0 g/dL"
}

print("=== SINGLE CALL ===")
print(single_call_rag(patient_result, dummy_llm))

print("\n=== MULTI CALL ===")
print(run_rag_pipeline(patient_result, dummy_llm))
