from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class StatusEnum(str, Enum):
    NORMAL = "NORMAL"
    BORDERLINE = "BORDERLINE"
    ABNORMAL = "ABNORMAL"


class TestResult(BaseModel):
    test: str
    value: str
    unit: str
    status: StatusEnum
    explanation: str
    advice: str


class ReportResponse(BaseModel):
    results: List[TestResult]
    summary: str
    see_doctor_urgently: bool
    disclaimer: str
    language: Optional[str] = "english"


class ChatRequest(BaseModel):
    question: str
    report_context: str
    language: Optional[str] = "english"


class ChatResponse(BaseModel):
    answer: str
    disclaimer: str