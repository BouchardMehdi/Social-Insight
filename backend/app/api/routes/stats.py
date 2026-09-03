from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_stats_service, get_workspace_context
from app.schemas.auth import WorkspaceContext
from app.schemas.stats import ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword
from app.services.stats import StatsService

router = APIRouter(prefix="/stats")


@router.get("/summary", response_model=SummaryStats)
def get_summary(
    context: WorkspaceContext = Depends(get_workspace_context),
    service: StatsService = Depends(get_stats_service),
) -> SummaryStats:
    return service.get_summary(context.workspace.id)


@router.get("/top-keywords", response_model=list[TopKeyword])
def get_top_keywords(
    limit: int = Query(default=10, ge=1, le=50),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: StatsService = Depends(get_stats_service),
) -> list[TopKeyword]:
    return service.get_top_keywords(context.workspace.id, limit=limit)


@router.get("/sentiments", response_model=SentimentDistribution)
def get_sentiments(
    context: WorkspaceContext = Depends(get_workspace_context),
    service: StatsService = Depends(get_stats_service),
) -> SentimentDistribution:
    return service.get_sentiments(context.workspace.id)


@router.get("/activity", response_model=list[ActivityPoint])
def get_activity(
    limit: int = Query(default=30, ge=1, le=365),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: StatsService = Depends(get_stats_service),
) -> list[ActivityPoint]:
    return service.get_activity(context.workspace.id, limit=limit)
