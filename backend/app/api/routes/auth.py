from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_auth_service, get_current_user, get_workspace_context
from app.core.exceptions import AuthorizationError
from app.schemas.auth import (
    AddWorkspaceMemberRequest,
    AuthResponse,
    CreateWorkspaceRequest,
    LoginRequest,
    RegisterRequest,
    SessionResponse,
    UserRecord,
    WorkspaceContext,
    WorkspaceMemberRead,
    WorkspaceRead,
)
from app.services.auth import AuthService

router = APIRouter()


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return service.register(payload)


@router.post("/auth/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return service.login(payload)


@router.get("/auth/me", response_model=SessionResponse)
def get_session(
    user: UserRecord = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> SessionResponse:
    return service.get_session(user)


@router.get("/workspaces", response_model=list[WorkspaceRead])
def list_workspaces(
    user: UserRecord = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> list[WorkspaceRead]:
    return service.get_session(user).workspaces


@router.post("/workspaces", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: CreateWorkspaceRequest,
    user: UserRecord = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> WorkspaceRead:
    return service.create_workspace(user, payload)


@router.get("/workspaces/{workspace_id}/members", response_model=list[WorkspaceMemberRead])
def list_workspace_members(
    workspace_id: str,
    context: WorkspaceContext = Depends(get_workspace_context),
    service: AuthService = Depends(get_auth_service),
) -> list[WorkspaceMemberRead]:
    if workspace_id != context.workspace.id:
        raise AuthorizationError()
    return service.list_workspace_members(context.user, workspace_id)


@router.post(
    "/workspaces/{workspace_id}/members",
    response_model=WorkspaceMemberRead,
    status_code=status.HTTP_201_CREATED,
)
def add_workspace_member(
    workspace_id: str,
    payload: AddWorkspaceMemberRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    service: AuthService = Depends(get_auth_service),
) -> WorkspaceMemberRead:
    if workspace_id != context.workspace.id:
        raise AuthorizationError()
    return service.add_workspace_member(context.user, workspace_id, payload)
