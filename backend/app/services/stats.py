from app.repositories.base import PostRepository
from app.schemas.stats import ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword


class StatsService:
    def __init__(self, repository: PostRepository) -> None:
        self.repository = repository

    def get_top_keywords(self, workspace_id: str, limit: int = 10) -> list[TopKeyword]:
        return self.repository.get_top_keywords(workspace_id, limit=limit)

    def get_sentiments(self, workspace_id: str) -> SentimentDistribution:
        return self.repository.get_sentiment_distribution(workspace_id)

    def get_activity(self, workspace_id: str, limit: int = 30) -> list[ActivityPoint]:
        return self.repository.get_daily_activity(workspace_id, limit=limit)

    def get_summary(self, workspace_id: str) -> SummaryStats:
        return self.repository.get_summary(workspace_id)
