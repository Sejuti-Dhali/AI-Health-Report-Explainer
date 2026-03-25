from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.ocr_engine import extract_text_from_file
from services.llm_parser import parse_report_values, answer_followup_question
from models.schemas import AnalysisResponse, ChatRequest, ChatResponse

router = APIRouter()


@router.post("/upload", response_model=AnalysisResponse)
async def upload_report(
    file: UploadFile = File(...),
    language: str = Form(default="english")
):
    try:
        file_bytes = await file.read()

        report_text = extract_text_from_file(file_bytes, file.content_type)

        if not report_text or len(report_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Could not extract text from file.")

        result = parse_report_values(report_text)


        return result

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