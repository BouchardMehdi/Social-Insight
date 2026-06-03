from functools import lru_cache

from app.config.settings import Settings, get_settings
from app.repositories.base import PostRepository
from app.repositories.bigquery import BigQueryPostRepository
from app.repositories.memory import InMemoryPostRepository
from app.services.nlp import NLPAnalyzer, SpacyNLPAnalyzer
from app.services.posts import PostService
from app.services.stats import StatsService


@lru_cache
def get_nlp_analyzer() -> NLPAnalyzer:
    return SpacyNLPAnalyzer()


@lru_cache
def get_post_repository() -> PostRepository:
    settings: Settings = get_settings()
    if settings.storage_backend == "memory":
        return InMemoryPostRepository()
    return BigQueryPostRepository(settings)


def get_post_service() -> PostService:
    return PostService(repository=get_post_repository(), analyzer=get_nlp_analyzer())


def get_stats_service() -> StatsService:
    return StatsService(repository=get_post_repository())
