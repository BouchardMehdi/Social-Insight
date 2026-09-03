from datetime import UTC, datetime
from uuid import uuid4

from app.repositories.base import PostRepository
from app.schemas.posts import PostCreate, PostFilters, PostListResponse, PostRead
from app.services.nlp import NLPAnalyzer


class PostService:
    def __init__(self, repository: PostRepository, analyzer: NLPAnalyzer) -> None:
        self.repository = repository
        self.analyzer = analyzer

    def create_post(self, workspace_id: str, payload: PostCreate) -> PostRead:
        analysis = self.analyzer.analyze(payload.content)
        now = datetime.now(UTC)
        post = PostRead(
            id=str(uuid4()),
            workspace_id=workspace_id,
            platform=payload.platform.lower(),
            author=payload.author,
            content=payload.content,
            language=analysis.language,
            sentiment=analysis.sentiment,
            keywords=analysis.keywords,
            created_at=now,
            inserted_at=now,
        )
        return self.repository.create_post(post)

    def list_posts(self, workspace_id: str, filters: PostFilters) -> PostListResponse:
        posts, total = self.repository.list_posts(workspace_id, filters)
        return PostListResponse(
            items=posts,
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def get_post(self, workspace_id: str, post_id: str) -> PostRead | None:
        return self.repository.get_post(workspace_id, post_id)
