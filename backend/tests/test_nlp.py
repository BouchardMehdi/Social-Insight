from fastapi.testclient import TestClient

from app.services.nlp import SpacyNLPAnalyzer


def test_analyze_positive_french_text(client: TestClient) -> None:
    response = client.post(
        "/api/analyze",
        json={"text": "L'intelligence artificielle transforme les entreprises."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "fr"
    assert payload["language_confidence"] >= 0.5
    assert payload["sentiment"] == "positive"
    assert payload["sentiment_confidence"] > 0.5
    assert payload["model_version"] == "spacy-rules-fr-en-v2"
    assert payload["analysis_status"] == "completed"
    assert "intelligence artificielle" in payload["keywords"]


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
    assert analysis.sentiment_confidence > 0.5
    assert len(analysis.keywords) == 3


def test_analyzer_handles_negation() -> None:
    analyzer = SpacyNLPAnalyzer()

    negative = analyzer.analyze("Ce produit n'est pas bon.")
    positive = analyzer.analyze("Ce produit n'est pas mauvais.")

    assert negative.sentiment == "negative"
    assert positive.sentiment == "positive"


def test_analyzer_detects_english_and_intensifiers() -> None:
    analyzer = SpacyNLPAnalyzer()

    analysis = analyzer.analyze("This product is really great and useful.")

    assert analysis.language == "en"
    assert analysis.language_confidence >= 0.5
    assert analysis.sentiment == "positive"
    assert analysis.sentiment_confidence >= 0.8


def test_analyzer_normalizes_accents_in_keywords() -> None:
    analyzer = SpacyNLPAnalyzer()

    analysis = analyzer.analyze("Une expérience géniale pour l'équipe produit.")

    assert analysis.sentiment == "positive"
    assert all("é" not in keyword for keyword in analysis.keywords)
