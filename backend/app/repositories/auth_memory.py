from app.repositories.auth_base import IdentityRepository
from app.schemas.auth import (
    MembershipRecord,
    UserRecord,
    WorkspaceMemberRead,
    WorkspaceRead,
    WorkspaceRecord,
)


class InMemoryIdentityRepository(IdentityRepository):
    def __init__(self) -> None:
        self._users: dict[str, UserRecord] = {}
        self._workspaces: dict[str, WorkspaceRecord] = {}
        self._memberships: dict[tuple[str, str], MembershipRecord] = {}

    def initialize(self) -> None:
        return None

    def get_user_by_email(self, email: str) -> UserRecord | None:
        return next((user for user in self._users.values() if user.email == email), None)

    def get_user_by_id(self, user_id: str) -> UserRecord | None:
        return self._users.get(user_id)

    def create_user_with_workspace(
        self,
        user: UserRecord,
        workspace: WorkspaceRecord,
        membership: MembershipRecord,
    ) -> None:
        self._users[user.id] = user
        self._workspaces[workspace.id] = workspace
        self._memberships[(membership.user_id, membership.workspace_id)] = membership

    def create_workspace(
        self, workspace: WorkspaceRecord, membership: MembershipRecord
    ) -> None:
        self._workspaces[workspace.id] = workspace
        self._memberships[(membership.user_id, membership.workspace_id)] = membership

    def list_user_workspaces(self, user_id: str) -> list[WorkspaceRead]:
        rows: list[WorkspaceRead] = []
        for (member_user_id, workspace_id), membership in self._memberships.items():
            if member_user_id != user_id:
                continue
            workspace = self._workspaces[workspace_id]
            rows.append(
                WorkspaceRead(
                    id=workspace.id,
                    name=workspace.name,
                    role=membership.role,
                    created_at=workspace.created_at,
                )
            )
        return sorted(rows, key=lambda row: row.created_at)

    def get_user_workspace(self, user_id: str, workspace_id: str) -> WorkspaceRead | None:
        membership = self._memberships.get((user_id, workspace_id))
        workspace = self._workspaces.get(workspace_id)
        if not membership or not workspace:
            return None
        return WorkspaceRead(
            id=workspace.id,
            name=workspace.name,
            role=membership.role,
            created_at=workspace.created_at,
        )

    def create_membership(self, membership: MembershipRecord) -> None:
        self._memberships[(membership.user_id, membership.workspace_id)] = membership

    def list_workspace_members(self, workspace_id: str) -> list[WorkspaceMemberRead]:
        rows: list[WorkspaceMemberRead] = []
        for (user_id, member_workspace_id), membership in self._memberships.items():
            if member_workspace_id != workspace_id:
                continue
            user = self._users[user_id]
            rows.append(
                WorkspaceMemberRead(
                    user_id=user.id,
                    email=user.email,
                    display_name=user.display_name,
                    role=membership.role,
                    joined_at=membership.created_at,
                )
            )
        role_order = {"owner": 0, "admin": 1, "member": 2}
        return sorted(rows, key=lambda row: (role_order[row.role], row.display_name.casefold()))
