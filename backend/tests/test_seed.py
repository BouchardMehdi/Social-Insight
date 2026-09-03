from app.repositories.memory import InMemoryPostRepository
from app.services.nlp import SpacyNLPAnalyzer
from app.services.seed import DemoSeedService


def test_demo_seed_generates_requested_volume() -> None:
    repository = InMemoryPostRepository()
    service = DemoSeedService(repository=repository, analyzer=SpacyNLPAnalyzer())

    workspace_id = "workspace-a"
    inserted = service.seed_if_needed(120, workspace_id)

    summary = repository.get_summary(workspace_id)
    sentiments = repository.get_sentiment_distribution(workspace_id)
    activity = repository.get_daily_activity(workspace_id, limit=90)

    assert inserted == 120
    assert summary.total_posts == 120
    assert summary.total_authors == 20
    assert sentiments.positive == 40
    assert sentiments.neutral == 40
    assert sentiments.negative == 40
    assert len(activity) > 20


def test_demo_seed_does_not_duplicate_existing_data() -> None:
    repository = InMemoryPostRepository()
    service = DemoSeedService(repository=repository, analyzer=SpacyNLPAnalyzer())

    workspace_id = "workspace-a"
    assert service.seed_if_needed(30, workspace_id) == 30
    assert service.seed_if_needed(30, workspace_id) == 0
    assert repository.get_summary(workspace_id).total_posts == 30
