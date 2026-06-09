from fastapi.testclient import TestClient


def test_error_response_contains_stable_contract_and_request_id(client: TestClient) -> None:
    response = client.get("/api/posts/missing-post", headers={"X-Request-ID": "test-request-123"})

    assert response.status_code == 404
    assert response.headers["X-Request-ID"] == "test-request-123"
    assert response.json() == {
        "error": {
            "code": "post_not_found",
            "message": "Post not found",
            "request_id": "test-request-123",
            "details": {"id": "missing-post"},
        }
    }


def test_validation_error_uses_stable_contract(client: TestClient) -> None:
    response = client.post(
        "/api/posts",
        json={"platform": "x", "author": "", "content": ""},
    )

    payload = response.json()
    assert response.status_code == 422
    assert response.headers["X-Request-ID"]
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Invalid request payload."
    assert payload["error"]["details"]


def test_success_response_contains_request_id_header(client: TestClient) -> None:
    response = client.get("/api/health", headers={"X-Request-ID": "healthy-request"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "healthy-request"
