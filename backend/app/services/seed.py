from datetime import UTC, datetime, timedelta
from random import Random
from uuid import NAMESPACE_URL, uuid5

from app.repositories.base import PostRepository
from app.schemas.posts import PostRead
from app.services.nlp import NLPAnalyzer


PLATFORMS = ["twitter", "linkedin", "reddit", "instagram", "youtube", "tiktok"]

AUTHORS = [
    "mehdi",
    "sarah_data",
    "nina_ai",
    "lucas_cloud",
    "amina_bi",
    "theo_dev",
    "lea_marketing",
    "yassine_ops",
    "camille_product",
    "noah_growth",
    "ines_nlp",
    "adam_saas",
    "emma_analytics",
    "samir_fintech",
    "jade_retail",
    "hugo_ia",
    "lina_startup",
    "malo_design",
    "sofia_crm",
    "raphael_data",
]

TOPICS = [
    "intelligence artificielle",
    "analyse de sentiment",
    "automatisation marketing",
    "cloud computing",
    "data engineering",
    "tableaux de bord",
    "experience client",
    "social listening",
    "strategie de contenu",
    "veille concurrentielle",
    "recommandation produit",
    "qualite des donnees",
    "pipeline analytics",
    "segmentation audience",
    "monitoring de marque",
    "API de donnees",
    "BigQuery",
    "FastAPI",
    "Vue.js",
    "NLP",
]

POSITIVE_TEMPLATES = [
    "L'innovation autour de {topic} transforme les entreprises et ameliore les decisions.",
    "{topic} devient vraiment utile pour les equipes data, les resultats sont excellents.",
    "Notre nouvelle approche {topic} est un succes et apporte une opportunite forte.",
    "Les clients trouvent {topic} genial, le gain de temps est positif pour toute l'equipe.",
    "Avec {topic}, les startups peuvent construire un produit plus innovant et reussi.",
]

NEUTRAL_TEMPLATES = [
    "Les equipes comparent plusieurs outils de {topic} pour structurer leur roadmap.",
    "Un benchmark sur {topic} montre des usages varies selon les secteurs.",
    "La conference du jour parle de {topic}, de donnees et de processus metier.",
    "Plusieurs entreprises testent {topic} dans un contexte de reporting interne.",
    "Le marche observe {topic} avec attention avant de choisir une solution.",
]

NEGATIVE_TEMPLATES = [
    "Le deploiement de {topic} reste difficile et cree un risque pour certaines equipes.",
    "Un probleme de qualite sur {topic} rend les analyses lentes et decevantes.",
    "Sans gouvernance, {topic} peut devenir un mauvais choix et generer une crise.",
    "Le projet {topic} rencontre un bug et l'experience utilisateur devient negative.",
    "Certaines entreprises parlent d'echec avec {topic} quand les donnees sont mal preparees.",
]

HASHTAGS = [
    "#data",
    "#ia",
    "#cloud",
    "#saas",
    "#analytics",
    "#startup",
    "#marketing",
    "#nlp",
]


class DemoSeedService:
    def __init__(self, repository: PostRepository, analyzer: NLPAnalyzer) -> None:
        self.repository = repository
        self.analyzer = analyzer

    def seed_if_needed(self, count: int) -> int:
        if count <= 0 or self.repository.get_summary().total_posts > 0:
            return 0

        posts = self.generate_posts(count)
        for post in posts:
            self.repository.create_post(post)
        return len(posts)

    def generate_posts(self, count: int) -> list[PostRead]:
        rng = Random(42)
        now = datetime.now(UTC)
        posts: list[PostRead] = []

        sentiment_templates = [
            ("positive", POSITIVE_TEMPLATES),
            ("neutral", NEUTRAL_TEMPLATES),
            ("negative", NEGATIVE_TEMPLATES),
        ]

        for index in range(count):
            _, templates = sentiment_templates[index % len(sentiment_templates)]
            topic = TOPICS[index % len(TOPICS)]
            template = templates[(index // len(sentiment_templates)) % len(templates)]
            hashtag = HASHTAGS[index % len(HASHTAGS)]
            platform = PLATFORMS[index % len(PLATFORMS)]
            author = AUTHORS[index % len(AUTHORS)]
            created_at = now - timedelta(
                days=rng.randint(0, 89),
                hours=rng.randint(0, 23),
                minutes=rng.randint(0, 59),
            )
            content = f"{template.format(topic=topic)} {hashtag}"
            analysis = self.analyzer.analyze(content)

            posts.append(
                PostRead(
                    id=str(uuid5(NAMESPACE_URL, f"social-insight-demo-post-{index}")),
                    platform=platform,
                    author=author,
                    content=content,
                    language=analysis.language,
                    sentiment=analysis.sentiment,
                    keywords=analysis.keywords,
                    created_at=created_at,
                    inserted_at=now,
                )
            )

        return sorted(posts, key=lambda post: post.created_at, reverse=True)
