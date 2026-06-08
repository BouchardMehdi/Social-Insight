from fastapi.testclient import TestClient


def create_post(
    client: TestClient,
    *,
    platform: str,
    author: str,
    content: str,
) -> dict:
    response = client.post(
        "/api/posts",
        json={"platform": platform, "author": author, "content": content},
    )
    assert response.status_code == 201
    return response.json()


def test_create_post_runs_nlp_and_normalizes_platform(client: TestClient) -> None:
    post = create_post(
        client,
        platform="Twitter",
        author="mehdi",
        content="L'intelligence artificielle transforme les entreprises.",
    )

    assert post["platform"] == "twitter"
    assert post["language"] == "fr"
    assert post["sentiment"] == "positive"
    assert post["keywords"]
    assert post["created_at"]
    assert post["inserted_at"]


def test_list_posts_supports_filters(client: TestClient) -> None:
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
        content="Le produit rencontre un probleme difficile et decevant.",
    )
    create_post(
        client,
        platform="reddit",
        author="nina",
        content="Les equipes comparent plusieurs outils de reporting interne.",
    )

    by_platform = client.get("/api/posts", params={"platform": "twitter"})
    by_sentiment = client.get("/api/posts", params={"sentiment": "negative"})
    by_keyword = client.get("/api/posts", params={"keyword": "intelligence artificielle"})

    assert by_platform.status_code == 200
    assert by_platform.json()["total"] == 1
    assert by_platform.json()["items"][0]["author"] == "mehdi"

    assert by_sentiment.status_code == 200
    assert by_sentiment.json()["total"] == 1
    assert by_sentiment.json()["items"][0]["sentiment"] == "negative"

    assert by_keyword.status_code == 200
    assert by_keyword.json()["total"] == 1
    assert "intelligence artificielle" in by_keyword.json()["items"][0]["keywords"]


def test_list_posts_is_paginated_and_ordered_by_creation_date(client: TestClient) -> None:
    created_posts = [
        create_post(
            client,
            platform="twitter",
            author=f"author_{index}",
            content=f"Une innovation utile pour les equipes data numero {index}.",
        )
        for index in range(5)
    ]

    first_page = client.get("/api/posts", params={"limit": 2, "offset": 0})
    second_page = client.get("/api/posts", params={"limit": 2, "offset": 2})

    assert first_page.status_code == 200
    assert first_page.json()["total"] == 5
    assert first_page.json()["limit"] == 2
    assert len(first_page.json()["items"]) == 2
    assert len(second_page.json()["items"]) == 2
    assert first_page.json()["items"][0]["id"] == created_posts[-1]["id"]
    assert {post["id"] for post in first_page.json()["items"]}.isdisjoint(
        {post["id"] for post in second_page.json()["items"]}
    )


def test_get_post_returns_404_for_unknown_id(client: TestClient) -> None:
    response = client.get("/api/posts/unknown-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_create_post_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post(
        "/api/posts",
        json={"platform": "x", "author": "", "content": ""},
    )

    assert response.status_code == 422
