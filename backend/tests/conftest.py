import os

os.environ["SOCIAL_INSIGHT_STORAGE_BACKEND"] = "memory"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def get_client() -> TestClient:
    return TestClient(app)
