from typing import Literal

from pydantic import BaseModel, Field

Sentiment = Literal["positive", "neutral", "negative"]


class AnalyzeRequest(BaseModel):
    text: str = Field(
        min_length=1,
        examples=["L'intelligence artificielle transforme les entreprises."],
    )


class AnalyzeResponse(BaseModel):
    language: str = Field(examples=["fr"])
    sentiment: Sentiment
    keywords: list[str]
