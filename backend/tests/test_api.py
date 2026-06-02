from tests.conftest import get_client


def test_healthcheck() -> None:
    with get_client() as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_analyze_text() -> None:
    with get_client() as client:
        response = client.post(
            "/api/analyze",
            json={"text": "L'intelligence artificielle transforme les entreprises."},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "fr"
    assert payload["sentiment"] == "positive"
    assert "intelligence artificielle" in payload["keywords"]


def test_create_list_and_get_post() -> None:
    with get_client() as client:
        created = client.post(
            "/api/posts",
            json={
                "platform": "twitter",
                "author": "mehdi",
                "content": "L'intelligence artificielle transforme les entreprises.",
            },
        )
        assert created.status_code == 201
        post = created.json()

        listed = client.get("/api/posts", params={"platform": "twitter", "limit": 10, "offset": 0})
        fetched = client.get(f"/api/posts/{post['id']}")

    assert listed.status_code == 200
    assert listed.json()["total"] >= 1
    assert fetched.status_code == 200
    assert fetched.json()["id"] == post["id"]


def test_stats_endpoints() -> None:
    with get_client() as client:
        client.post(
            "/api/posts",
            json={
                "platform": "linkedin",
                "author": "sarah",
                "content": "Une innovation utile pour les équipes data.",
            },
        )
        keywords = client.get("/api/stats/top-keywords")
        sentiments = client.get("/api/stats/sentiments")
        activity = client.get("/api/stats/activity")
        summary = client.get("/api/stats/summary")

    assert keywords.status_code == 200
    assert sentiments.status_code == 200
    assert activity.status_code == 200
    assert summary.status_code == 200
    assert summary.json()["total_posts"] >= 1
