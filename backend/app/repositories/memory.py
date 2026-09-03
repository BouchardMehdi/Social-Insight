from collections import Counter
from operator import attrgetter
from threading import RLock

from app.repositories.base import PostRepository
from app.schemas.nlp import AnalysisStatus, AnalyzeResponse
from app.schemas.posts import PostFilters, PostRead
from app.schemas.stats import ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword


class InMemoryPostRepository(PostRepository):
    """Development and test repository. Production data belongs in BigQuery."""

    def __init__(self) -> None:
        self._posts: list[PostRead] = []
        self._lock = RLock()

    def initialize(self) -> None:
        return None

    def create_post(self, post: PostRead) -> PostRead:
        with self._lock:
            self._posts.append(post.model_copy(deep=True))
        return post

    def set_analysis_status(
        self,
        workspace_id: str,
        post_id: str,
        status: AnalysisStatus,
        error: str | None = None,
    ) -> bool:
        with self._lock:
            post = self._find_post(workspace_id, post_id)
            if not post:
                return False
            post.analysis_status = status
            post.analysis_error = error
            return True

    def complete_post_analysis(
        self, workspace_id: str, post_id: str, analysis: AnalyzeResponse
    ) -> bool:
        with self._lock:
            post = self._find_post(workspace_id, post_id)
            if not post:
                return False
            post.language = analysis.language
            post.language_confidence = analysis.language_confidence
            post.sentiment = analysis.sentiment
            post.sentiment_confidence = analysis.sentiment_confidence
            post.keywords = list(analysis.keywords)
            post.model_version = analysis.model_version
            post.analysis_status = "completed"
            post.analysis_error = None
            return True

    def list_incomplete_posts(self, limit: int = 1000) -> list[PostRead]:
        with self._lock:
            return [
                post.model_copy(deep=True)
                for post in self._posts
                if post.analysis_status in {"pending", "processing"}
            ][:limit]

    def list_posts(self, workspace_id: str, filters: PostFilters) -> tuple[list[PostRead], int]:
        with self._lock:
            posts = [
                post.model_copy(deep=True)
                for post in self._apply_filters(workspace_id, filters)
            ]
        total = len(posts)
        ordered = sorted(posts, key=attrgetter("created_at"), reverse=True)
        return ordered[filters.offset : filters.offset + filters.limit], total

    def get_post(self, workspace_id: str, post_id: str) -> PostRead | None:
        with self._lock:
            post = self._find_post(workspace_id, post_id)
            return post.model_copy(deep=True) if post else None

    def get_top_keywords(self, workspace_id: str, limit: int = 10) -> list[TopKeyword]:
        with self._lock:
            counts = Counter(
                keyword
                for post in self._posts
                if post.workspace_id == workspace_id and post.analysis_status == "completed"
                for keyword in post.keywords
            )
        return [
            TopKeyword(keyword=keyword, count=count)
            for keyword, count in counts.most_common(limit)
        ]

    def get_sentiment_distribution(self, workspace_id: str) -> SentimentDistribution:
        with self._lock:
            counts = Counter(
                post.sentiment
                for post in self._posts
                if post.workspace_id == workspace_id and post.analysis_status == "completed"
            )
        return SentimentDistribution(
            positive=counts["positive"],
            neutral=counts["neutral"],
            negative=counts["negative"],
        )

    def get_daily_activity(self, workspace_id: str, limit: int = 30) -> list[ActivityPoint]:
        with self._lock:
            counts = Counter(
                post.created_at.date().isoformat()
                for post in self._posts
                if post.workspace_id == workspace_id and post.analysis_status == "completed"
            )
        rows = [ActivityPoint(date=date, count=count) for date, count in sorted(counts.items())]
        return rows[-limit:]

    def get_summary(self, workspace_id: str) -> SummaryStats:
        with self._lock:
            posts = [post for post in self._posts if post.workspace_id == workspace_id]
        authors = {post.author for post in posts}
        return SummaryStats(total_posts=len(posts), total_authors=len(authors))

    def _apply_filters(self, workspace_id: str, filters: PostFilters) -> list[PostRead]:
        posts = [post for post in self._posts if post.workspace_id == workspace_id]
        if filters.platform:
            posts = [post for post in posts if post.platform == filters.platform]
        if filters.sentiment:
            posts = [
                post
                for post in posts
                if post.analysis_status == "completed" and post.sentiment == filters.sentiment
            ]
        if filters.keyword:
            normalized = filters.keyword.lower()
            posts = [post for post in posts if normalized in {kw.lower() for kw in post.keywords}]
        return posts

    def _find_post(self, workspace_id: str, post_id: str) -> PostRead | None:
        return next(
            (
                post
                for post in self._posts
                if post.id == post_id and post.workspace_id == workspace_id
            ),
            None,
        )
