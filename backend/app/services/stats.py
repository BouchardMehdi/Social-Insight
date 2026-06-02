from app.repositories.base import PostRepository
from app.schemas.stats import ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword


class StatsService:
    def __init__(self, repository: PostRepository) -> None:
        self.repository = repository

    def get_top_keywords(self, limit: int = 10) -> list[TopKeyword]:
        return self.repository.get_top_keywords(limit=limit)

    def get_sentiments(self) -> SentimentDistribution:
        return self.repository.get_sentiment_distribution()

    def get_activity(self, limit: int = 30) -> list[ActivityPoint]:
        return self.repository.get_daily_activity(limit=limit)

    def get_summary(self) -> SummaryStats:
        return self.repository.get_summary()
