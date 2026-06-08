from fastapi.testclient import TestClient

from app.services.nlp import SpacyNLPAnalyzer


def test_analyze_positive_french_text(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        json={"text": "L'intelligence artificielle transforme les entreprises."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "language": "fr",
        "sentiment": "positive",
        "keywords": [
            "intelligence artificielle transforme",
            "artificielle transforme entreprises",
            "intelligence artificielle",
            "artificielle transforme",
            "transforme entreprises",
            "intelligence",
            "artificielle",
            "transforme",
        ],
    }


def test_analyze_negative_text(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        json={"text": "Le produit rencontre un probleme difficile et decevant."},
    )

    assert response.status_code == 200
    assert response.json()["sentiment"] == "negative"


def test_analyze_neutral_text(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        json={"text": "Les equipes comparent plusieurs outils de reporting interne."},
    )

    assert response.status_code == 200
    assert response.json()["sentiment"] == "neutral"


def test_analyze_rejects_empty_text(client: TestClient) -> None:
    response = client.post("/api/analyze", json={"text": ""})

    assert response.status_code == 422


def test_nlp_analyzer_can_be_used_without_api() -> None:
    analyzer = SpacyNLPAnalyzer(max_keywords=3)

    analysis = analyzer.analyze("Une innovation utile pour les equipes data.")

    assert analysis.language == "fr"
    assert analysis.sentiment == "positive"
    assert len(analysis.keywords) == 3
