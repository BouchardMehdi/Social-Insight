from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_stats_service
from app.schemas.stats import ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword
from app.services.stats import StatsService

router = APIRouter(prefix="/stats")


@router.get("/summary", response_model=SummaryStats)
def get_summary(service: StatsService = Depends(get_stats_service)) -> SummaryStats:
    return service.get_summary()


@router.get("/top-keywords", response_model=list[TopKeyword])
def get_top_keywords(
    limit: int = Query(default=10, ge=1, le=50),
    service: StatsService = Depends(get_stats_service),
) -> list[TopKeyword]:
    return service.get_top_keywords(limit=limit)


@router.get("/sentiments", response_model=SentimentDistribution)
def get_sentiments(service: StatsService = Depends(get_stats_service)) -> SentimentDistribution:
    return service.get_sentiments()


@router.get("/activity", response_model=list[ActivityPoint])
def get_activity(
    limit: int = Query(default=30, ge=1, le=365),
    service: StatsService = Depends(get_stats_service),
) -> list[ActivityPoint]:
    return service.get_activity(limit=limit)
