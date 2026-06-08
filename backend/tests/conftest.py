import os
from collections.abc import Iterator

os.environ["SOCIAL_INSIGHT_STORAGE_BACKEND"] = "memory"
os.environ["SOCIAL_INSIGHT_SEED_ON_STARTUP"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.dependencies import get_nlp_analyzer, get_post_repository  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client() -> Iterator[TestClient]:
    get_post_repository.cache_clear()
    get_nlp_analyzer.cache_clear()
    with TestClient(app) as test_client:
        yield test_client
    get_post_repository.cache_clear()
    get_nlp_analyzer.cache_clear()


def get_client() -> TestClient:
    return TestClient(app)
