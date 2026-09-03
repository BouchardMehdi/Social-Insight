from datetime import datetime

from google.api_core.exceptions import GoogleAPICallError, NotFound
from google.cloud import bigquery

from app.config.settings import Settings
from app.core.exceptions import RepositoryError, StorageConfigurationError
from app.repositories.auth_base import IdentityRepository
from app.schemas.auth import (
    MembershipRecord,
    UserRecord,
    WorkspaceMemberRead,
    WorkspaceRead,
    WorkspaceRecord,
)


class BigQueryIdentityRepository(IdentityRepository):
    def __init__(self, settings: Settings) -> None:
        if not settings.google_cloud_project:
            raise StorageConfigurationError(
                "SOCIAL_INSIGHT_GOOGLE_CLOUD_PROJECT is required for BigQuery storage."
            )
        if settings.google_application_credentials:
            self.client = bigquery.Client.from_service_account_json(
                settings.google_application_credentials,
                project=settings.google_cloud_project,
            )
        else:
            self.client = bigquery.Client(project=settings.google_cloud_project)

        dataset_id = f"{settings.google_cloud_project}.{settings.bigquery_dataset}"
        self.users_table_id = f"{dataset_id}.{settings.bigquery_users_table}"
        self.workspaces_table_id = f"{dataset_id}.{settings.bigquery_workspaces_table}"
        self.memberships_table_id = f"{dataset_id}.{settings.bigquery_memberships_table}"

    def initialize(self) -> None:
        self._ensure_table(self.users_table_id, self._users_schema())
        self._ensure_table(self.workspaces_table_id, self._workspaces_schema())
        self._ensure_table(self.memberships_table_id, self._memberships_schema())

    def get_user_by_email(self, email: str) -> UserRecord | None:
        sql = f"""
            SELECT id, email, password_hash, display_name, created_at
            FROM `{self.users_table_id}`
            WHERE email = @email
            LIMIT 1
        """
        rows = self.client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("email", "STRING", email)]
            ),
        ).result()
        row = next(iter(rows), None)
        return self._row_to_user(row) if row else None

    def get_user_by_id(self, user_id: str) -> UserRecord | None:
        sql = f"""
            SELECT id, email, password_hash, display_name, created_at
            FROM `{self.users_table_id}`
            WHERE id = @user_id
            LIMIT 1
        """
        rows = self.client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
            ),
        ).result()
        row = next(iter(rows), None)
        return self._row_to_user(row) if row else None

    def create_user_with_workspace(
        self,
        user: UserRecord,
        workspace: WorkspaceRecord,
        membership: MembershipRecord,
    ) -> None:
        self._load_rows(self.users_table_id, [user.model_dump(mode="json")], self._users_schema())
        self.create_workspace(workspace, membership)

    def create_workspace(
        self, workspace: WorkspaceRecord, membership: MembershipRecord
    ) -> None:
        self._load_rows(
            self.workspaces_table_id,
            [workspace.model_dump(mode="json")],
            self._workspaces_schema(),
        )
        self._load_rows(
            self.memberships_table_id,
            [membership.model_dump(mode="json")],
            self._memberships_schema(),
        )

    def list_user_workspaces(self, user_id: str) -> list[WorkspaceRead]:
        sql = f"""
            SELECT w.id, w.name, m.role, w.created_at
            FROM `{self.memberships_table_id}` AS m
            JOIN `{self.workspaces_table_id}` AS w ON w.id = m.workspace_id
            WHERE m.user_id = @user_id
            ORDER BY w.created_at ASC
        """
        rows = self.client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
            ),
        ).result()
        return [self._row_to_workspace(row) for row in rows]

    def get_user_workspace(self, user_id: str, workspace_id: str) -> WorkspaceRead | None:
        sql = f"""
            SELECT w.id, w.name, m.role, w.created_at
            FROM `{self.memberships_table_id}` AS m
            JOIN `{self.workspaces_table_id}` AS w ON w.id = m.workspace_id
            WHERE m.user_id = @user_id AND m.workspace_id = @workspace_id
            LIMIT 1
        """
        rows = self.client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                    bigquery.ScalarQueryParameter("workspace_id", "STRING", workspace_id),
                ]
            ),
        ).result()
        row = next(iter(rows), None)
        return self._row_to_workspace(row) if row else None

    def create_membership(self, membership: MembershipRecord) -> None:
        self._load_rows(
            self.memberships_table_id,
            [membership.model_dump(mode="json")],
            self._memberships_schema(),
        )

    def list_workspace_members(self, workspace_id: str) -> list[WorkspaceMemberRead]:
        sql = f"""
            SELECT u.id AS user_id, u.email, u.display_name, m.role, m.created_at AS joined_at
            FROM `{self.memberships_table_id}` AS m
            JOIN `{self.users_table_id}` AS u ON u.id = m.user_id
            WHERE m.workspace_id = @workspace_id
            ORDER BY
                CASE m.role WHEN 'owner' THEN 0 WHEN 'admin' THEN 1 ELSE 2 END,
                u.display_name ASC
        """
        rows = self.client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("workspace_id", "STRING", workspace_id)
                ]
            ),
        ).result()
        return [
            WorkspaceMemberRead(
                user_id=row.user_id,
                email=row.email,
                display_name=row.display_name,
                role=row.role,
                joined_at=self._to_datetime(row.joined_at),
            )
            for row in rows
        ]

    def _ensure_table(self, table_id: str, schema: list[bigquery.SchemaField]) -> None:
        try:
            self.client.get_table(table_id)
        except NotFound:
            self.client.create_table(bigquery.Table(table_id, schema=schema))

    def _load_rows(
        self,
        table_id: str,
        rows: list[dict[str, object]],
        schema: list[bigquery.SchemaField],
    ) -> None:
        try:
            job = self.client.load_table_from_json(
                rows,
                table_id,
                job_config=bigquery.LoadJobConfig(
                    schema=schema,
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                ),
            )
            job.result()
        except GoogleAPICallError as exc:
            raise RepositoryError("BigQuery identity write failed.", details=str(exc)) from exc

    @staticmethod
    def _users_schema() -> list[bigquery.SchemaField]:
        return [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("password_hash", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("display_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]

    @staticmethod
    def _workspaces_schema() -> list[bigquery.SchemaField]:
        return [
            bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]

    @staticmethod
    def _memberships_schema() -> list[bigquery.SchemaField]:
        return [
            bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("workspace_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("role", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]

    @staticmethod
    def _row_to_user(row: bigquery.table.Row) -> UserRecord:
        return UserRecord(
            id=row.id,
            email=row.email,
            password_hash=row.password_hash,
            display_name=row.display_name,
            created_at=BigQueryIdentityRepository._to_datetime(row.created_at),
        )

    @staticmethod
    def _row_to_workspace(row: bigquery.table.Row) -> WorkspaceRead:
        return WorkspaceRead(
            id=row.id,
            name=row.name,
            role=row.role,
            created_at=BigQueryIdentityRepository._to_datetime(row.created_at),
        )

    @staticmethod
    def _to_datetime(value: datetime | str) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
