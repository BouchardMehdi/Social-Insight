from typing import Literal

from pydantic import BaseModel, Field

Sentiment = Literal["positive", "neutral", "negative"]
AnalysisStatus = Literal["pending", "processing", "completed", "failed"]


class AnalyzeRequest(BaseModel):
    text: str = Field(
        min_length=1,
        examples=["L'intelligence artificielle transforme les entreprises."],
    )


class AnalyzeResponse(BaseModel):
    language: str = Field(examples=["fr"])
    language_confidence: float = Field(ge=0, le=1)
    sentiment: Sentiment
    sentiment_confidence: float = Field(ge=0, le=1)
    keywords: list[str]
    model_version: str
    analysis_status: AnalysisStatus = "completed"
