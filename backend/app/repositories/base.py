from abc import ABC, abstractmethod

from app.schemas.nlp import AnalysisStatus, AnalyzeResponse
from app.schemas.posts import PostFilters, PostRead
from app.schemas.stats import ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword


class PostRepository(ABC):
    @abstractmethod
    def initialize(self) -> None:
        """Create required datastore resources if they do not exist."""

    @abstractmethod
    def create_post(self, post: PostRead) -> PostRead:
        """Persist a social post."""

    @abstractmethod
    def set_analysis_status(
        self,
        workspace_id: str,
        post_id: str,
        status: AnalysisStatus,
        error: str | None = None,
    ) -> bool:
        """Update the processing status of one post."""

    @abstractmethod
    def complete_post_analysis(
        self, workspace_id: str, post_id: str, analysis: AnalyzeResponse
    ) -> bool:
        """Persist the completed NLP result for one post."""

    @abstractmethod
    def list_incomplete_posts(self, limit: int = 1000) -> list[PostRead]:
        """Return pending or interrupted posts so workers can resume them."""

    @abstractmethod
    def list_posts(self, workspace_id: str, filters: PostFilters) -> tuple[list[PostRead], int]:
        """Return filtered posts and the total count before pagination."""

    @abstractmethod
    def get_post(self, workspace_id: str, post_id: str) -> PostRead | None:
        """Return one post by id."""

    @abstractmethod
    def get_top_keywords(self, workspace_id: str, limit: int = 10) -> list[TopKeyword]:
        """Return the most common keywords."""

    @abstractmethod
    def get_sentiment_distribution(self, workspace_id: str) -> SentimentDistribution:
        """Return post counts by sentiment."""

    @abstractmethod
    def get_daily_activity(self, workspace_id: str, limit: int = 30) -> list[ActivityPoint]:
        """Return daily post activity."""

    @abstractmethod
    def get_summary(self, workspace_id: str) -> SummaryStats:
        """Return high-level dashboard counters."""
