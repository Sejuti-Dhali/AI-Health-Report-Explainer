from services.rag.rag_pipeline import run_rag_pipeline
from services.personalization.apply import attach_personalization
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.ocr_engine import extract_text_from_file
from services.llm_parser import parse_report_values, answer_followup_question
from services.risk_engine import evaluate_test
from models.schemas import ChatRequest, ChatResponse

router = APIRouter()


def llm_callable(prompt: str) -> str:
    return answer_followup_question(question=prompt, report_context="")


def _fallback_enrich_result(item: dict, reason: str = ""):
    item["confidence_score"] = 0.0
    item["confidence_band"] = "low"
    item["vote_ratio"] = 0.0
    item["semantic_agreement"] = 0.0
    item["needs_manual_review"] = True
    item["retrieved_evidence"] = []
    item["hallucination_flag"] = False
    item["evidence_support"] = False
    item["evidence_support_score"] = 0.0

    old_expl = item.get("explanation", "") or ""
    if reason:
        item["explanation"] = f"{old_expl} [Fallback mode: RAG unavailable - {reason}]".strip()
    else:
        item["explanation"] = f"{old_expl} [Fallback mode: RAG unavailable]".strip()

    return item


def _rag_enrich_result(item: dict, llm_callable_fn):
    patient_result = {
        "test": item.get("test", ""),
        "value": item.get("value", ""),
        "unit": item.get("unit", ""),
        "reference": item.get("reference", ""),
    }

    try:
        rag_result = run_rag_pipeline(patient_result, llm_callable_fn)

        item["status"] = rag_result.get("final_status", item.get("status", "unknown"))
        item["explanation"] = rag_result.get("final_explanation", item.get("explanation", ""))
        item["confidence_score"] = rag_result.get("confidence", {}).get("confidence")
        item["confidence_band"] = rag_result.get("confidence", {}).get("confidence_band")
        item["vote_ratio"] = rag_result.get("confidence", {}).get("vote_ratio")
        item["semantic_agreement"] = rag_result.get("confidence", {}).get("semantic_agreement")
        item["needs_manual_review"] = rag_result.get("needs_manual_review", False)
        item["retrieved_evidence"] = rag_result.get("retrieved_evidence", [])
        item["hallucination_flag"] = rag_result.get("hallucination", {}).get("hallucination_flag", False)
        item["evidence_support"] = rag_result.get("hallucination", {}).get("evidence_support", False)
        item["evidence_support_score"] = rag_result.get("hallucination", {}).get("evidence_support_score", 0.0)

        return item

    except Exception as e:
        return _fallback_enrich_result(item, str(e))


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    language: str = Form(default="english"),
    age: int = Form(default=45),
    sex: str = Form(default="female"),
    bmi: float = Form(default=24.5),
    condition: str = Form(default="none")
):
    try:
        file_bytes = await file.read()
        report_text = extract_text_from_file(file_bytes, file.content_type)

        if not report_text or len(report_text.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Could not extract enough text from this file. For scanned PDFs or unclear images, try a clearer file."
            )

        parsed = parse_report_values(report_text)

        patient_ctx = {
            "age": age,
            "sex": sex,
            "bmi": bmi,
            "condition": condition,
        }

        enriched_results = []
        for p in parsed.parameters:
            benchmark = evaluate_test(p.name, p.value, sex="general", age_group="adult")

            base_item = {
                "test": p.name,
                "value": p.value,
                "unit": p.unit,
                "status": p.status.value if hasattr(p.status, "value") else str(p.status),
                "reference": p.reference_range,
                "explanation": p.explanation,
                "source_label": benchmark.get("source_label"),
                "source_type": benchmark.get("source_type"),
                "confidence": benchmark.get("confidence"),
                "interpretation_mode": benchmark.get("interpretation_mode"),
            }

            rag_item = _rag_enrich_result(base_item, llm_callable)
            final_item = attach_personalization(rag_item, patient_ctx)
            enriched_results.append(final_item)

        return {
            "results": enriched_results,
            "summary": parsed.risk_summary.summary,
            "see_doctor_urgently": parsed.risk_summary.level.lower() == "high",
            "risk_level": parsed.risk_summary.level,
            "disclaimer": parsed.disclaimer,
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_followup(req: ChatRequest):
    try:
        answer = answer_followup_question(
            question=req.question,
            report_context=req.report_context
        )
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
