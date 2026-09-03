from collections import Counter

from app.services.bigquery_seed import BigQuerySeedFactory
from app.services.nlp import SpacyNLPAnalyzer


def test_bigquery_seed_generates_diverse_non_uniform_data() -> None:
    posts = BigQuerySeedFactory(analyzer=SpacyNLPAnalyzer()).generate_posts(
        1000, "workspace-a"
    )

    sentiments = Counter(post.sentiment for post in posts)
    platforms = Counter(post.platform for post in posts)
    authors = Counter(post.author for post in posts)
    keywords = Counter(keyword for post in posts for keyword in post.keywords)

    assert len(posts) == 1000
    assert {post.workspace_id for post in posts} == {"workspace-a"}
    assert len(platforms) >= 5
    assert len(authors) >= 15
    assert len(keywords) > 50
    assert sentiments["positive"] > sentiments["neutral"] > sentiments["negative"]
    assert platforms["twitter"] > platforms["linkedin"] > platforms["tiktok"]
    assert keywords.most_common(1)[0][1] > keywords.most_common(10)[-1][1]
