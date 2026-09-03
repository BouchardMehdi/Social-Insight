import logging
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock

from app.repositories.base import PostRepository
from app.schemas.posts import PostRead
from app.services.nlp import NLPAnalyzer

logger = logging.getLogger(__name__)


class AnalysisTaskManager:
    """Run NLP jobs outside request threads and recover unfinished persisted jobs."""

    def __init__(
        self,
        repository: PostRepository,
        analyzer: NLPAnalyzer,
        max_workers: int = 2,
    ) -> None:
        self.repository = repository
        self.analyzer = analyzer
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="social-insight-nlp",
        )
        self._active: set[tuple[str, str]] = set()
        self._lock = Lock()

    def submit(self, post: PostRead) -> bool:
        key = (post.workspace_id, post.id)
        with self._lock:
            if key in self._active:
                return False
            self._active.add(key)

        try:
            future = self.executor.submit(self._process, post.model_copy(deep=True))
        except RuntimeError:
            with self._lock:
                self._active.discard(key)
            raise
        future.add_done_callback(lambda completed: self._release(key, completed))
        return True

    def recover_incomplete(self, limit: int = 1000) -> int:
        return sum(self.submit(post) for post in self.repository.list_incomplete_posts(limit))

    def shutdown(self) -> None:
        self.executor.shutdown(wait=True, cancel_futures=False)

    def _process(self, post: PostRead) -> None:
        try:
            self.repository.set_analysis_status(
                post.workspace_id, post.id, "processing", error=None
            )
            analysis = self.analyzer.analyze(post.content)
            if not self.repository.complete_post_analysis(post.workspace_id, post.id, analysis):
                logger.warning(
                    "analysis_post_missing",
                    extra={"workspace_id": post.workspace_id, "post_id": post.id},
                )
                return
            logger.info(
                "analysis_completed",
                extra={
                    "workspace_id": post.workspace_id,
                    "post_id": post.id,
                    "model_version": analysis.model_version,
                },
            )
        except Exception as exc:
            logger.exception(
                "analysis_failed",
                extra={"workspace_id": post.workspace_id, "post_id": post.id},
            )
            try:
                self.repository.set_analysis_status(
                    post.workspace_id,
                    post.id,
                    "failed",
                    error=str(exc)[:1000] or "Unknown NLP analysis error.",
                )
            except Exception:
                logger.exception(
                    "analysis_failure_status_update_failed",
                    extra={"workspace_id": post.workspace_id, "post_id": post.id},
                )

    def _release(self, key: tuple[str, str], _: Future[None]) -> None:
        with self._lock:
            self._active.discard(key)
