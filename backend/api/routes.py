from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from backend.services.ocr_engine import extract_text
from backend.services.llm_parser import analyze_report, answer_question
from backend.models.schemas import ReportResponse, ChatRequest, ChatResponse

router = APIRouter()


@router.post("/upload", response_model=ReportResponse)
async def upload_report(
    file: UploadFile = File(...),
    language: str = Form(default="english")
):
    try:
        file_bytes = await file.read()
        report_text = extract_text(file_bytes, file.filename)

        if not report_text or len(report_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Could not extract text from file.")

        result = analyze_report(report_text, language)
        result["language"] = language
        return JSONResponse(content=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = answer_question(
            request.question,
            request.report_context,
            request.language
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/health")
async def health():
    return {"status": "ok"}
