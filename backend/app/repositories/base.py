from abc import ABC, abstractmethod

from app.schemas.posts import PostFilters, PostRead
from app.schemas.stats import ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword


class PostRepository(ABC):
    @abstractmethod
    def initialize(self) -> None:
        """Create required datastore resources if they do not exist."""

    @abstractmethod
    def create_post(self, post: PostRead) -> PostRead:
        """Persist an analyzed social post."""

    @abstractmethod
    def list_posts(self, filters: PostFilters) -> tuple[list[PostRead], int]:
        """Return filtered posts and the total count before pagination."""

    @abstractmethod
    def get_post(self, post_id: str) -> PostRead | None:
        """Return one post by id."""

    @abstractmethod
    def get_top_keywords(self, limit: int = 10) -> list[TopKeyword]:
        """Return the most common keywords."""

    @abstractmethod
    def get_sentiment_distribution(self) -> SentimentDistribution:
        """Return post counts by sentiment."""

    @abstractmethod
    def get_daily_activity(self, limit: int = 30) -> list[ActivityPoint]:
        """Return daily post activity."""

    @abstractmethod
    def get_summary(self) -> SummaryStats:
        """Return high-level dashboard counters."""
