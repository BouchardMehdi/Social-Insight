from datetime import UTC, datetime
from uuid import uuid4

from app.config.settings import Settings
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.auth_base import IdentityRepository
from app.schemas.auth import (
    AddWorkspaceMemberRequest,
    AuthResponse,
    CreateWorkspaceRequest,
    LoginRequest,
    MembershipRecord,
    RegisterRequest,
    SessionResponse,
    UserRead,
    UserRecord,
    WorkspaceMemberRead,
    WorkspaceRead,
    WorkspaceRecord,
)


class AuthService:
    def __init__(self, repository: IdentityRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings

    def register(self, payload: RegisterRequest) -> AuthResponse:
        if self.repository.get_user_by_email(payload.email):
            raise ConflictError("email_already_registered", "This email is already registered.")

        now = datetime.now(UTC)
        user = UserRecord(
            id=str(uuid4()),
            email=payload.email,
            password_hash=hash_password(payload.password),
            display_name=payload.display_name.strip(),
            created_at=now,
        )
        workspace = WorkspaceRecord(
            id=str(uuid4()),
            name=(payload.workspace_name or f"Espace de {user.display_name}").strip(),
            created_at=now,
        )
        membership = MembershipRecord(
            user_id=user.id,
            workspace_id=workspace.id,
            role="owner",
            created_at=now,
        )
        self.repository.create_user_with_workspace(user, workspace, membership)
        return self._build_auth_response(user)

    def login(self, payload: LoginRequest) -> AuthResponse:
        user = self.repository.get_user_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        return self._build_auth_response(user)

    def get_session(self, user: UserRecord) -> SessionResponse:
        workspaces = self.repository.list_user_workspaces(user.id)
        if not workspaces:
            raise AuthenticationError("No workspace is available for this account.")
        return SessionResponse(
            user=self._public_user(user),
            workspaces=workspaces,
            active_workspace_id=workspaces[0].id,
        )

    def create_workspace(
        self, user: UserRecord, payload: CreateWorkspaceRequest
    ) -> WorkspaceRead:
        now = datetime.now(UTC)
        workspace = WorkspaceRecord(id=str(uuid4()), name=payload.name.strip(), created_at=now)
        membership = MembershipRecord(
            user_id=user.id,
            workspace_id=workspace.id,
            role="owner",
            created_at=now,
        )
        self.repository.create_workspace(workspace, membership)
        return WorkspaceRead(
            id=workspace.id,
            name=workspace.name,
            role=membership.role,
            created_at=workspace.created_at,
        )

    def ensure_demo_account(self) -> SessionResponse:
        user = self.repository.get_user_by_email(self.settings.demo_email)
        if user:
            return self.get_session(user)
        response = self.register(
            RegisterRequest(
                email=self.settings.demo_email,
                password=self.settings.demo_password,
                display_name=self.settings.demo_display_name,
                workspace_name=self.settings.demo_workspace_name,
            )
        )
        return SessionResponse(
            user=response.user,
            workspaces=response.workspaces,
            active_workspace_id=response.active_workspace_id,
        )

    def list_workspace_members(
        self, user: UserRecord, workspace_id: str
    ) -> list[WorkspaceMemberRead]:
        if not self.repository.get_user_workspace(user.id, workspace_id):
            raise AuthorizationError()
        return self.repository.list_workspace_members(workspace_id)

    def add_workspace_member(
        self,
        actor: UserRecord,
        workspace_id: str,
        payload: AddWorkspaceMemberRequest,
    ) -> WorkspaceMemberRead:
        actor_workspace = self.repository.get_user_workspace(actor.id, workspace_id)
        if not actor_workspace or actor_workspace.role == "member":
            raise AuthorizationError("Only workspace owners and admins can add members.")
        if payload.role == "admin" and actor_workspace.role != "owner":
            raise AuthorizationError("Only the workspace owner can add an admin.")

        target = self.repository.get_user_by_email(payload.email)
        if not target:
            raise NotFoundError(resource="user", identifier=payload.email)
        if self.repository.get_user_workspace(target.id, workspace_id):
            raise ConflictError(
                "workspace_member_exists", "This user already belongs to the workspace."
            )

        membership = MembershipRecord(
            user_id=target.id,
            workspace_id=workspace_id,
            role=payload.role,
            created_at=datetime.now(UTC),
        )
        self.repository.create_membership(membership)
        return WorkspaceMemberRead(
            user_id=target.id,
            email=target.email,
            display_name=target.display_name,
            role=membership.role,
            joined_at=membership.created_at,
        )

    def _build_auth_response(self, user: UserRecord) -> AuthResponse:
        session = self.get_session(user)
        token, expires_in = create_access_token(
            user_id=user.id,
            secret_key=self.settings.auth_secret_key,
            expires_minutes=self.settings.auth_token_expire_minutes,
            issuer=self.settings.auth_token_issuer,
        )
        return AuthResponse(
            **session.model_dump(),
            access_token=token,
            expires_in=expires_in,
        )

    @staticmethod
    def _public_user(user: UserRecord) -> UserRead:
        return UserRead(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            created_at=user.created_at,
        )
