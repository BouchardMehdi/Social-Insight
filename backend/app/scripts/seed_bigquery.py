import argparse
import logging

from app.config.settings import get_settings
from app.repositories.bigquery import BigQueryPostRepository
from app.services.bigquery_seed import BigQuerySeedFactory
from app.services.nlp import SpacyNLPAnalyzer

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed Social Insight demo data into BigQuery.")
    parser.add_argument("--count", type=int, default=1000, help="Number of posts to generate.")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace the posts table content instead of appending rows.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count <= 0:
        raise SystemExit("--count must be greater than 0")

    settings = get_settings()
    repository = BigQueryPostRepository(settings)
    repository.initialize()

    posts = BigQuerySeedFactory(analyzer=SpacyNLPAnalyzer()).generate_posts(args.count)
    inserted = repository.create_posts(posts, replace=args.replace)
    mode = "replaced" if args.replace else "appended"
    logger.warning("Seed %s %s BigQuery posts.", mode, inserted)
    print(f"Seed {mode}: {inserted} posts inserted into BigQuery.")


if __name__ == "__main__":
    main()
