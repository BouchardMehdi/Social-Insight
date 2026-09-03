from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import Settings, get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.repositories.auth_base import IdentityRepository
from app.repositories.auth_bigquery import BigQueryIdentityRepository
from app.repositories.auth_memory import InMemoryIdentityRepository
from app.repositories.base import PostRepository
from app.repositories.bigquery import BigQueryPostRepository
from app.repositories.memory import InMemoryPostRepository
from app.schemas.auth import UserRecord, WorkspaceContext
from app.services.analysis_tasks import AnalysisTaskManager
from app.services.auth import AuthService
from app.services.nlp import NLPAnalyzer, SpacyNLPAnalyzer
from app.services.posts import PostService
from app.services.stats import StatsService

bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_nlp_analyzer() -> NLPAnalyzer:
    return SpacyNLPAnalyzer()


@lru_cache
def get_post_repository() -> PostRepository:
    settings: Settings = get_settings()
    if settings.storage_backend == "memory":
        return InMemoryPostRepository()
    return BigQueryPostRepository(settings)


@lru_cache
def get_identity_repository() -> IdentityRepository:
    settings: Settings = get_settings()
    if settings.storage_backend == "memory":
        return InMemoryIdentityRepository()
    return BigQueryIdentityRepository(settings)


def get_auth_service() -> AuthService:
    return AuthService(repository=get_identity_repository(), settings=get_settings())


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    repository: Annotated[IdentityRepository, Depends(get_identity_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserRecord:
    if not credentials or credentials.scheme.casefold() != "bearer":
        raise AuthenticationError()
    user_id = decode_access_token(
        credentials.credentials,
        secret_key=settings.auth_secret_key,
        issuer=settings.auth_token_issuer,
    )
    user = repository.get_user_by_id(user_id)
    if not user:
        raise AuthenticationError("The authenticated user no longer exists.")
    return user


def get_workspace_context(
    x_workspace_id: Annotated[str, Header(alias="X-Workspace-ID")],
    user: Annotated[UserRecord, Depends(get_current_user)],
    repository: Annotated[IdentityRepository, Depends(get_identity_repository)],
) -> WorkspaceContext:
    workspace = repository.get_user_workspace(user.id, x_workspace_id)
    if not workspace:
        raise AuthorizationError()
    return WorkspaceContext(user=user, workspace=workspace)


def get_analysis_task_manager(request: Request) -> AnalysisTaskManager:
    return request.app.state.analysis_task_manager


def get_post_service(request: Request) -> PostService:
    return PostService(
        repository=get_post_repository(),
        analyzer=get_nlp_analyzer(),
        task_manager=get_analysis_task_manager(request),
    )


def get_stats_service() -> StatsService:
    return StatsService(repository=get_post_repository())
