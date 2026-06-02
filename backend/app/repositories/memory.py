from collections import Counter
from operator import attrgetter

from app.repositories.base import PostRepository
from app.schemas.posts import PostFilters, PostRead
from app.schemas.stats import ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword


class InMemoryPostRepository(PostRepository):
    """Development and test repository. Production data belongs in BigQuery."""

    def __init__(self) -> None:
        self._posts: list[PostRead] = []

    def initialize(self) -> None:
        return None

    def create_post(self, post: PostRead) -> PostRead:
        self._posts.append(post)
        return post

    def list_posts(self, filters: PostFilters) -> tuple[list[PostRead], int]:
        posts = self._apply_filters(filters)
        total = len(posts)
        ordered = sorted(posts, key=attrgetter("created_at"), reverse=True)
        return ordered[filters.offset : filters.offset + filters.limit], total

    def get_post(self, post_id: str) -> PostRead | None:
        return next((post for post in self._posts if post.id == post_id), None)

    def get_top_keywords(self, limit: int = 10) -> list[TopKeyword]:
        counts = Counter(keyword for post in self._posts for keyword in post.keywords)
        return [TopKeyword(keyword=keyword, count=count) for keyword, count in counts.most_common(limit)]

    def get_sentiment_distribution(self) -> SentimentDistribution:
        counts = Counter(post.sentiment for post in self._posts)
        return SentimentDistribution(
            positive=counts["positive"],
            neutral=counts["neutral"],
            negative=counts["negative"],
        )

    def get_daily_activity(self, limit: int = 30) -> list[ActivityPoint]:
        counts = Counter(post.created_at.date().isoformat() for post in self._posts)
        rows = [ActivityPoint(date=date, count=count) for date, count in sorted(counts.items())]
        return rows[-limit:]

    def get_summary(self) -> SummaryStats:
        authors = {post.author for post in self._posts}
        return SummaryStats(total_posts=len(self._posts), total_authors=len(authors))

    def _apply_filters(self, filters: PostFilters) -> list[PostRead]:
        posts = self._posts
        if filters.platform:
            posts = [post for post in posts if post.platform == filters.platform]
        if filters.sentiment:
            posts = [post for post in posts if post.sentiment == filters.sentiment]
        if filters.keyword:
            normalized = filters.keyword.lower()
            posts = [post for post in posts if normalized in {kw.lower() for kw in post.keywords}]
        return posts
