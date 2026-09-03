from datetime import UTC, datetime, timedelta
from random import Random
from uuid import NAMESPACE_URL, uuid5

from app.schemas.posts import PostRead
from app.services.nlp import NLPAnalyzer
from app.services.seed import (
    AUTHORS,
    HASHTAGS,
    NEGATIVE_TEMPLATES,
    NEUTRAL_TEMPLATES,
    POSITIVE_TEMPLATES,
)

WEIGHTED_TOPICS = [
    ("intelligence artificielle", 16),
    ("analyse de sentiment", 12),
    ("social listening", 10),
    ("cloud computing", 9),
    ("data engineering", 8),
    ("BigQuery", 7),
    ("automatisation marketing", 7),
    ("experience client", 6),
    ("pipeline analytics", 6),
    ("veille concurrentielle", 5),
    ("FastAPI", 4),
    ("Vue.js", 3),
    ("NLP", 3),
    ("monitoring de marque", 2),
    ("qualite des donnees", 2),
]

WEIGHTED_SENTIMENTS = [
    ("positive", 58),
    ("neutral", 27),
    ("negative", 15),
]

WEIGHTED_PLATFORMS = [
    ("twitter", 35),
    ("linkedin", 24),
    ("reddit", 15),
    ("instagram", 12),
    ("youtube", 9),
    ("tiktok", 5),
]

CAMPAIGNS = [
    "lancement produit",
    "retour client",
    "benchmark marche",
    "strategie contenu",
    "pilotage data",
    "veille marque",
    "reporting executif",
    "croissance SaaS",
]


class BigQuerySeedFactory:
    def __init__(self, analyzer: NLPAnalyzer, seed: int = 20260611) -> None:
        self.analyzer = analyzer
        self.rng = Random(seed)

    def generate_posts(self, count: int, workspace_id: str) -> list[PostRead]:
        now = datetime.now(UTC)
        posts: list[PostRead] = []

        for index in range(count):
            sentiment = self._weighted_choice(WEIGHTED_SENTIMENTS)
            platform = self._weighted_choice(WEIGHTED_PLATFORMS)
            topic = self._weighted_choice(WEIGHTED_TOPICS)
            author = self.rng.choice(AUTHORS)
            campaign = self.rng.choice(CAMPAIGNS)
            hashtag = self.rng.choice(HASHTAGS)
            template = self._template_for_sentiment(sentiment)
            created_at = now - timedelta(
                days=self.rng.triangular(0, 119, 18),
                hours=self.rng.randint(0, 23),
                minutes=self.rng.randint(0, 59),
            )
            content = (
                f"{template.format(topic=topic)} "
                f"Contexte: {campaign}. Signal observe sur {platform}. {hashtag}"
            )
            analysis = self.analyzer.analyze(content)

            posts.append(
                PostRead(
                    id=str(uuid5(NAMESPACE_URL, f"social-insight-bigquery-seed-{index}")),
                    workspace_id=workspace_id,
                    platform=platform,
                    author=author,
                    content=content,
                    language=analysis.language,
                    language_confidence=analysis.language_confidence,
                    sentiment=analysis.sentiment,
                    sentiment_confidence=analysis.sentiment_confidence,
                    keywords=analysis.keywords,
                    model_version=analysis.model_version,
                    analysis_status=analysis.analysis_status,
                    analysis_error=None,
                    created_at=created_at,
                    inserted_at=now,
                )
            )

        return sorted(posts, key=lambda post: post.created_at, reverse=True)

    def _template_for_sentiment(self, sentiment: str) -> str:
        if sentiment == "positive":
            return self.rng.choice(POSITIVE_TEMPLATES)
        if sentiment == "negative":
            return self.rng.choice(NEGATIVE_TEMPLATES)
        return self.rng.choice(NEUTRAL_TEMPLATES)

    def _weighted_choice(self, values: list[tuple[str, int]]) -> str:
        total = sum(weight for _, weight in values)
        cursor = self.rng.uniform(0, total)
        cumulative = 0.0
        for value, weight in values:
            cumulative += weight
            if cursor <= cumulative:
                return value
        return values[-1][0]
