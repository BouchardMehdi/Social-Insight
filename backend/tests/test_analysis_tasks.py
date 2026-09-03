from datetime import UTC, datetime
from threading import Event

from app.repositories.memory import InMemoryPostRepository
from app.schemas.nlp import AnalyzeResponse
from app.schemas.posts import PostRead
from app.services.analysis_tasks import AnalysisTaskManager
from app.services.nlp import NLPAnalyzer, SpacyNLPAnalyzer


class FailingAnalyzer(NLPAnalyzer):
    def analyze(self, text: str) -> AnalyzeResponse:
        raise RuntimeError("model unavailable")


class BlockingAnalyzer(NLPAnalyzer):
    def __init__(self) -> None:
        self.started = Event()
        self.release = Event()

    def analyze(self, text: str) -> AnalyzeResponse:
        self.started.set()
        self.release.wait(timeout=2)
        return SpacyNLPAnalyzer().analyze(text)


def pending_post(post_id: str = "post-1") -> PostRead:
    now = datetime.now(UTC)
    return PostRead(
        id=post_id,
        workspace_id="workspace-1",
        platform="twitter",
        author="ada",
        content="Une innovation vraiment utile.",
        language="unknown",
        language_confidence=0,
        sentiment="neutral",
        sentiment_confidence=0,
        keywords=[],
        model_version="spacy-rules-fr-en-v2",
        analysis_status="pending",
        analysis_error=None,
        created_at=now,
        inserted_at=now,
    )


def test_task_manager_completes_analysis() -> None:
    repository = InMemoryPostRepository()
    post = repository.create_post(pending_post())
    manager = AnalysisTaskManager(repository, SpacyNLPAnalyzer(), max_workers=1)

    assert manager.submit(post) is True
    manager.shutdown()

    completed = repository.get_post(post.workspace_id, post.id)
    assert completed is not None
    assert completed.analysis_status == "completed"
    assert completed.sentiment == "positive"
    assert completed.keywords


def test_task_manager_marks_failures() -> None:
    repository = InMemoryPostRepository()
    post = repository.create_post(pending_post())
    manager = AnalysisTaskManager(repository, FailingAnalyzer(), max_workers=1)

    manager.submit(post)
    manager.shutdown()

    failed = repository.get_post(post.workspace_id, post.id)
    assert failed is not None
    assert failed.analysis_status == "failed"
    assert failed.analysis_error == "model unavailable"


def test_task_manager_exposes_processing_status() -> None:
    repository = InMemoryPostRepository()
    post = repository.create_post(pending_post())
    analyzer = BlockingAnalyzer()
    manager = AnalysisTaskManager(repository, analyzer, max_workers=1)

    manager.submit(post)
    assert analyzer.started.wait(timeout=1)
    processing = repository.get_post(post.workspace_id, post.id)
    assert processing is not None
    assert processing.analysis_status == "processing"

    analyzer.release.set()
    manager.shutdown()
    completed = repository.get_post(post.workspace_id, post.id)
    assert completed is not None
    assert completed.analysis_status == "completed"


def test_task_manager_recovers_incomplete_posts() -> None:
    repository = InMemoryPostRepository()
    repository.create_post(pending_post("post-to-recover"))
    manager = AnalysisTaskManager(repository, SpacyNLPAnalyzer(), max_workers=1)

    assert manager.recover_incomplete() == 1
    manager.shutdown()

    recovered = repository.get_post("workspace-1", "post-to-recover")
    assert recovered is not None
    assert recovered.analysis_status == "completed"
