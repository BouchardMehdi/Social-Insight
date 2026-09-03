import os
from collections.abc import Iterator

os.environ["SOCIAL_INSIGHT_STORAGE_BACKEND"] = "memory"
os.environ["SOCIAL_INSIGHT_SEED_ON_STARTUP"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.dependencies import (  # noqa: E402
    get_identity_repository,
    get_nlp_analyzer,
    get_post_repository,
)
from app.main import app  # noqa: E402


@pytest.fixture
def client() -> Iterator[TestClient]:
    get_post_repository.cache_clear()
    get_identity_repository.cache_clear()
    get_nlp_analyzer.cache_clear()
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "test-password-123",
                "display_name": "Test User",
                "workspace_name": "Test Workspace",
            },
        )
        payload = response.json()
        test_client.headers.update(
            {
                "Authorization": f"Bearer {payload['access_token']}",
                "X-Workspace-ID": payload["active_workspace_id"],
            }
        )
        yield test_client
    get_post_repository.cache_clear()
    get_identity_repository.cache_clear()
    get_nlp_analyzer.cache_clear()


@pytest.fixture
def anonymous_client() -> Iterator[TestClient]:
    get_post_repository.cache_clear()
    get_identity_repository.cache_clear()
    get_nlp_analyzer.cache_clear()
    with TestClient(app) as test_client:
        yield test_client
    get_post_repository.cache_clear()
    get_identity_repository.cache_clear()
    get_nlp_analyzer.cache_clear()


def get_client() -> TestClient:
    return TestClient(app)
