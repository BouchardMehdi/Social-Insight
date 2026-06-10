from datetime import datetime

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from app.config.settings import Settings
from app.core.exceptions import RepositoryError, StorageConfigurationError
from app.repositories.base import PostRepository
from app.schemas.posts import PostFilters, PostRead
from app.schemas.stats import ActivityPoint, SentimentDistribution, SummaryStats, TopKeyword


class BigQueryPostRepository(PostRepository):
    def __init__(self, settings: Settings) -> None:
        if not settings.google_cloud_project:
            raise StorageConfigurationError(
                "SOCIAL_INSIGHT_GOOGLE_CLOUD_PROJECT is required for BigQuery storage."
            )

        self.settings = settings
        self.client = bigquery.Client(project=settings.google_cloud_project)
        self.dataset_id = f"{settings.google_cloud_project}.{settings.bigquery_dataset}"
        self.table_id = f"{self.dataset_id}.{settings.bigquery_posts_table}"

    def initialize(self) -> None:
        self._ensure_dataset()
        self._ensure_posts_table()

    def create_post(self, post: PostRead) -> PostRead:
        payload = post.model_dump(mode="json")
        errors = self.client.insert_rows_json(self.table_id, [payload])
        if errors:
            raise RepositoryError("BigQuery insertion failed.", details=errors)
        return post

    def list_posts(self, filters: PostFilters) -> tuple[list[PostRead], int]:
        where_sql, params = self._build_filters(filters)
        params.extend(
            [
                bigquery.ScalarQueryParameter("limit", "INT64", filters.limit),
                bigquery.ScalarQueryParameter("offset", "INT64", filters.offset),
            ]
        )

        count_sql = f"SELECT COUNT(*) AS total FROM `{self.table_id}` {where_sql}"
        count_job = self.client.query(
            count_sql,
            job_config=bigquery.QueryJobConfig(query_parameters=params[:-2]),
        )
        total = next(iter(count_job.result())).total

        sql = f"""
            SELECT
                id,
                platform,
                author,
                content,
                language,
                sentiment,
                keywords,
                created_at,
                inserted_at
            FROM `{self.table_id}`
            {where_sql}
            ORDER BY created_at DESC
            LIMIT @limit OFFSET @offset
        """
        rows = self.client.query(
            sql,
            job_config=bigquery.QueryJobConfig(query_parameters=params),
        ).result()
        return [self._row_to_post(row) for row in rows], int(total)

    def get_post(self, post_id: str) -> PostRead | None:
        sql = f"""
            SELECT
                id,
                platform,
                author,
                content,
                language,
                sentiment,
                keywords,
                created_at,
                inserted_at
            FROM `{self.table_id}`
            WHERE id = @post_id
            LIMIT 1
        """
        rows = self.client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("post_id", "STRING", post_id)]
            ),
        ).result()
        row = next(iter(rows), None)
        return self._row_to_post(row) if row else None

    def get_top_keywords(self, limit: int = 10) -> list[TopKeyword]:
        sql = f"""
            SELECT keyword, COUNT(*) AS count
            FROM `{self.table_id}`, UNNEST(keywords) AS keyword
            GROUP BY keyword
            ORDER BY count DESC, keyword ASC
            LIMIT @limit
        """
        rows = self.client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("limit", "INT64", limit)]
            ),
        ).result()
        return [TopKeyword(keyword=row.keyword, count=int(row.count)) for row in rows]

    def get_sentiment_distribution(self) -> SentimentDistribution:
        sql = f"""
            SELECT sentiment, COUNT(*) AS count
            FROM `{self.table_id}`
            GROUP BY sentiment
        """
        rows = self.client.query(sql).result()
        counts = {row.sentiment: int(row.count) for row in rows}
        return SentimentDistribution(
            positive=counts.get("positive", 0),
            neutral=counts.get("neutral", 0),
            negative=counts.get("negative", 0),
        )

    def get_daily_activity(self, limit: int = 30) -> list[ActivityPoint]:
        sql = f"""
            SELECT FORMAT_DATE('%F', DATE(created_at)) AS date, COUNT(*) AS count
            FROM `{self.table_id}`
            GROUP BY date
            ORDER BY date DESC
            LIMIT @limit
        """
        rows = self.client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("limit", "INT64", limit)]
            ),
        ).result()
        return [ActivityPoint(date=row.date, count=int(row.count)) for row in reversed(list(rows))]

    def get_summary(self) -> SummaryStats:
        sql = f"""
            SELECT COUNT(*) AS total_posts, COUNT(DISTINCT author) AS total_authors
            FROM `{self.table_id}`
        """
        row = next(iter(self.client.query(sql).result()))
        return SummaryStats(total_posts=int(row.total_posts), total_authors=int(row.total_authors))

    def _ensure_dataset(self) -> None:
        dataset = bigquery.Dataset(self.dataset_id)
        dataset.location = self.settings.bigquery_location
        try:
            self.client.get_dataset(self.dataset_id)
        except NotFound:
            self.client.create_dataset(dataset)

    def _ensure_posts_table(self) -> None:
        schema = [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("platform", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("author", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("content", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("language", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sentiment", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("keywords", "STRING", mode="REPEATED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("inserted_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        table = bigquery.Table(self.table_id, schema=schema)
        try:
            self.client.get_table(self.table_id)
        except NotFound:
            self.client.create_table(table)

    def _build_filters(
        self, filters: PostFilters
    ) -> tuple[str, list[bigquery.ScalarQueryParameter]]:
        conditions: list[str] = []
        params: list[bigquery.ScalarQueryParameter] = []

        if filters.platform:
            conditions.append("platform = @platform")
            params.append(bigquery.ScalarQueryParameter("platform", "STRING", filters.platform))
        if filters.sentiment:
            conditions.append("sentiment = @sentiment")
            params.append(bigquery.ScalarQueryParameter("sentiment", "STRING", filters.sentiment))
        if filters.keyword:
            conditions.append("@keyword IN UNNEST(keywords)")
            params.append(
                bigquery.ScalarQueryParameter("keyword", "STRING", filters.keyword.lower())
            )

        return (f"WHERE {' AND '.join(conditions)}" if conditions else ""), params

    @staticmethod
    def _row_to_post(row: bigquery.table.Row) -> PostRead:
        def to_datetime(value: datetime | str) -> datetime:
            if isinstance(value, datetime):
                return value
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        return PostRead(
            id=row.id,
            platform=row.platform,
            author=row.author,
            content=row.content,
            language=row.language,
            sentiment=row.sentiment,
            keywords=list(row.keywords or []),
            created_at=to_datetime(row.created_at),
            inserted_at=to_datetime(row.inserted_at),
        )
