from fastapi.testclient import TestClient

from tests.test_posts_api import create_post


def test_stats_are_calculated_from_inserted_posts(client: TestClient) -> None:
    create_post(
        client,
        platform="twitter",
        author="mehdi",
        content="L'intelligence artificielle transforme les entreprises.",
    )
    create_post(
        client,
        platform="linkedin",
        author="sarah",
        content="Une innovation utile pour les equipes data.",
    )
    create_post(
        client,
        platform="reddit",
        author="mehdi",
        content="Le produit rencontre un probleme difficile et decevant.",
    )

    summary = client.get("/api/stats/summary")
    sentiments = client.get("/api/stats/sentiments")
    keywords = client.get("/api/stats/top-keywords", params={"limit": 5})
    activity = client.get("/api/stats/activity", params={"limit": 7})

    assert summary.status_code == 200
    assert summary.json() == {"total_posts": 3, "total_authors": 2}

    assert sentiments.status_code == 200
    assert sentiments.json() == {"positive": 2, "neutral": 0, "negative": 1}

    assert keywords.status_code == 200
    assert len(keywords.json()) <= 5
    assert keywords.json()[0]["count"] >= 1

    assert activity.status_code == 200
    assert activity.json()[0]["count"] == 3


def test_stats_return_empty_values_without_posts(client: TestClient) -> None:
    summary = client.get("/api/stats/summary")
    sentiments = client.get("/api/stats/sentiments")
    keywords = client.get("/api/stats/top-keywords")
    activity = client.get("/api/stats/activity")

    assert summary.json() == {"total_posts": 0, "total_authors": 0}
    assert sentiments.json() == {"positive": 0, "neutral": 0, "negative": 0}
    assert keywords.json() == []
    assert activity.json() == []
