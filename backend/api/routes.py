from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.ocr_engine import extract_text_from_file
from services.llm_parser import parse_report_values, answer_followup_question
from services.risk_engine import evaluate_test
from models.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    language: str = Form(default="english")
):
    try:
        file_bytes = await file.read()
        report_text = extract_text_from_file(file_bytes, file.content_type)

        if not report_text or len(report_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Could not extract text from file.")

        parsed = parse_report_values(report_text)

        enriched_results = []
        for p in parsed.parameters:
            benchmark = evaluate_test(p.name, p.value, sex="general", age_group="adult")
            enriched_results.append(
                {
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
            )

        return {
            "results": enriched_results,
            "summary": parsed.risk_summary.summary,
            "see_doctor_urgently": parsed.risk_summary.level.lower() == "high",
            "risk_level": parsed.risk_summary.level,
            "disclaimer": parsed.disclaimer,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = answer_followup_question(
            request.question,
            request.report_context
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "ok"}
