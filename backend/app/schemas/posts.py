from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.nlp import AnalysisStatus, Sentiment


class PostCreate(BaseModel):
    platform: str = Field(min_length=2, max_length=50, examples=["twitter"])
    author: str = Field(min_length=1, max_length=100, examples=["mehdi"])
    content: str = Field(
        min_length=1,
        max_length=5000,
        examples=["L'intelligence artificielle transforme les entreprises."],
    )


class PostRead(BaseModel):
    id: str
    workspace_id: str
    platform: str
    author: str
    content: str
    language: str
    language_confidence: float = Field(ge=0, le=1)
    sentiment: Sentiment
    sentiment_confidence: float = Field(ge=0, le=1)
    keywords: list[str]
    model_version: str
    analysis_status: AnalysisStatus = "completed"
    analysis_error: str | None = None
    created_at: datetime
    inserted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostListResponse(BaseModel):
    items: list[PostRead]
    total: int
    limit: int
    offset: int


class PostFilters(BaseModel):
    platform: str | None = None
    sentiment: Literal["positive", "neutral", "negative"] | None = None
    keyword: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
