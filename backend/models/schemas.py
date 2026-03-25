from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class RangeStatus(str, Enum):
    HIGH = "high"
    LOW = "low"
    NORMAL = "normal"
    UNKNOWN = "unknown"


class ReportParameter(BaseModel):
    name: str = Field(..., description="Name of the test parameter, e.g. 'Hemoglobin'")
    value: str = Field(..., description="Measured value, e.g. '10.2'")
    unit: Optional[str] = Field(None, description="Unit, e.g. 'g/dL'")
    reference_range: Optional[str] = Field(None, description="Normal range, e.g. '12–17 g/dL'")
    status: RangeStatus = Field(..., description="high | low | normal | unknown")
    explanation: Optional[str] = Field(None, description="Simple plain-language explanation")


class RiskSummary(BaseModel):
    level: str = Field(..., description="Overall risk level: Low / Moderate / High")
    summary: str = Field(..., description="Short plain-English risk summary")
    recommendations: List[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    parameters: List[ReportParameter]
    risk_summary: RiskSummary
    disclaimer: str = (
        "This analysis is AI-generated and intended for informational purposes only. "
        "Please consult a qualified medical professional before making any health decisions."
    )


class ChatRequest(BaseModel):
    question: str = Field(..., description="User's follow-up question")
    report_context: Optional[str] = Field(
        None, description="Stringified report parameters for context"
    )


class ChatResponse(BaseModel):
    answer: str


class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate into Bangla")


class TranslationResponse(BaseModel):
    translated_text: str