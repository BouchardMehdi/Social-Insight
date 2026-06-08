from app.repositories.memory import InMemoryPostRepository
from app.services.nlp import SpacyNLPAnalyzer
from app.services.seed import DemoSeedService


def test_demo_seed_generates_requested_volume() -> None:
    repository = InMemoryPostRepository()
    service = DemoSeedService(repository=repository, analyzer=SpacyNLPAnalyzer())

    inserted = service.seed_if_needed(120)

    summary = repository.get_summary()
    sentiments = repository.get_sentiment_distribution()
    activity = repository.get_daily_activity(limit=90)

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

    assert service.seed_if_needed(30) == 30
    assert service.seed_if_needed(30) == 0
    assert repository.get_summary().total_posts == 30
