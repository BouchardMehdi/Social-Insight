from datetime import UTC, datetime
from uuid import uuid4

from app.repositories.base import PostRepository
from app.schemas.posts import PostCreate, PostFilters, PostListResponse, PostRead
from app.services.analysis_tasks import AnalysisTaskManager
from app.services.nlp import NLPAnalyzer


class PostService:
    def __init__(
        self,
        repository: PostRepository,
        analyzer: NLPAnalyzer,
        task_manager: AnalysisTaskManager,
    ) -> None:
        self.repository = repository
        self.analyzer = analyzer
        self.task_manager = task_manager

    def create_post(self, workspace_id: str, payload: PostCreate) -> PostRead:
        now = datetime.now(UTC)
        post = PostRead(
            id=str(uuid4()),
            workspace_id=workspace_id,
            platform=payload.platform.lower(),
            author=payload.author,
            content=payload.content,
            language="unknown",
            language_confidence=0,
            sentiment="neutral",
            sentiment_confidence=0,
            keywords=[],
            model_version=getattr(self.analyzer, "model_version", "pending"),
            analysis_status="pending",
            analysis_error=None,
            created_at=now,
            inserted_at=now,
        )
        persisted = self.repository.create_post(post)
        self.task_manager.submit(persisted)
        return persisted

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
