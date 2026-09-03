from abc import ABC, abstractmethod

from app.schemas.auth import (
    MembershipRecord,
    UserRecord,
    WorkspaceMemberRead,
    WorkspaceRead,
    WorkspaceRecord,
)


class IdentityRepository(ABC):
    @abstractmethod
    def initialize(self) -> None:
        """Create the identity datastore resources if needed."""

    @abstractmethod
    def get_user_by_email(self, email: str) -> UserRecord | None:
        """Return a user by normalized email."""

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> UserRecord | None:
        """Return a user by id."""

    @abstractmethod
    def create_user_with_workspace(
        self,
        user: UserRecord,
        workspace: WorkspaceRecord,
        membership: MembershipRecord,
    ) -> None:
        """Create a user and their first workspace."""

    @abstractmethod
    def create_workspace(
        self, workspace: WorkspaceRecord, membership: MembershipRecord
    ) -> None:
        """Create a workspace and its owner membership."""

    @abstractmethod
    def list_user_workspaces(self, user_id: str) -> list[WorkspaceRead]:
        """Return all workspaces accessible to a user."""

    @abstractmethod
    def get_user_workspace(self, user_id: str, workspace_id: str) -> WorkspaceRead | None:
        """Return one accessible workspace, including the membership role."""

    @abstractmethod
    def create_membership(self, membership: MembershipRecord) -> None:
        """Add an existing user to a workspace."""

    @abstractmethod
    def list_workspace_members(self, workspace_id: str) -> list[WorkspaceMemberRead]:
        """Return the members of a workspace."""
