
from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import (
    AnalysisResponse,
    ChatRequest,
    ChatResponse,
    TranslationRequest,
    TranslationResponse,
)
from services.ocr_engine import extract_text_from_file
from services.llm_parser import (
    parse_report_values,
    answer_followup_question,
    translate_to_bangla,
)

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse, tags=["Report"])
async def analyze_report(file: UploadFile = File(...)):
    """
    Upload a medical report (PDF or image).
    Extracts text via OCR, parses values via LLM, returns color-coded results.
    """
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or image (PNG/JPEG).",
        )

    file_bytes = await file.read()

    # Step 1: OCR — extract raw text from file
    raw_text = extract_text_from_file(file_bytes, file.content_type)

    if not raw_text or len(raw_text.strip()) < 10:
        raise HTTPException(
            status_code=422,
            detail="Could not extract readable text from the uploaded file.",
        )

    # Step 2: LLM — parse values, flag ranges, generate summary
    analysis = parse_report_values(raw_text)

    return analysis


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat_followup(request: ChatRequest):
    """
    Accept a follow-up question about the analyzed report.
    Returns a plain-language explanation.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    answer = answer_followup_question(
        question=request.question,
        report_context=request.report_context,
    )
    return ChatResponse(answer=answer)


@router.post("/translate", response_model=TranslationResponse, tags=["Translation"])
def translate_report(request: TranslationRequest):
    """
    Translate analysis results or explanations to Bangla.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text to translate cannot be empty.")

    translated = translate_to_bangla(request.text)
    return TranslationResponse(translated_text=translated)