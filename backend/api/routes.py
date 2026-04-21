from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.ocr_engine import extract_text_from_file
from services.local_cbc_parser import parse_local_cbc_report
from services.personalization.apply import attach_personalization
from services.llm_parser import answer_followup_question
from models.schemas import ChatRequest, ChatResponse

router = APIRouter()


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

        parsed = parse_local_cbc_report(report_text, sex=sex)

        patient_ctx = {
            "age": age,
            "sex": sex,
            "bmi": bmi,
            "condition": condition,
        }

        final_results = []
        for item in parsed["results"]:
            final_results.append(attach_personalization(item, patient_ctx))

        return {
            "results": final_results,
            "summary": parsed["summary"],
            "see_doctor_urgently": parsed["see_doctor_urgently"],
            "risk_level": parsed["risk_level"],
            "disclaimer": parsed["disclaimer"],
            "analysis_mode": "local_cbc_parser_with_personalization",
            "rag_enabled": False
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
    except Exception:
        return ChatResponse(
            answer="Follow-up chat is temporarily unavailable. The upload analysis remains available in local parser mode."
        )
