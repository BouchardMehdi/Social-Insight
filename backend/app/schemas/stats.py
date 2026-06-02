from pydantic import BaseModel


class TopKeyword(BaseModel):
    keyword: str
    count: int


class SentimentDistribution(BaseModel):
    positive: int = 0
    neutral: int = 0
    negative: int = 0


class ActivityPoint(BaseModel):
    date: str
    count: int


class SummaryStats(BaseModel):
    total_posts: int
    total_authors: int
