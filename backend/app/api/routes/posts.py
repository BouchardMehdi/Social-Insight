from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_post_service, get_workspace_context
from app.core.exceptions import NotFoundError
from app.schemas.auth import WorkspaceContext
from app.schemas.nlp import Sentiment
from app.schemas.posts import PostCreate, PostFilters, PostListResponse, PostRead
from app.services.posts import PostService

router = APIRouter(prefix="/posts")


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    context: WorkspaceContext = Depends(get_workspace_context),
    service: PostService = Depends(get_post_service),
) -> PostRead:
    return service.create_post(context.workspace.id, payload)


@router.get("", response_model=PostListResponse)
def list_posts(
    platform: str | None = None,
    sentiment: Sentiment | None = None,
    keyword: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: PostService = Depends(get_post_service),
) -> PostListResponse:
    filters = PostFilters(
        platform=platform,
        sentiment=sentiment,
        keyword=keyword,
        limit=limit,
        offset=offset,
    )
    return service.list_posts(context.workspace.id, filters)


@router.get("/{post_id}", response_model=PostRead)
def get_post(
    post_id: str,
    context: WorkspaceContext = Depends(get_workspace_context),
    service: PostService = Depends(get_post_service),
) -> PostRead:
    post = service.get_post(context.workspace.id, post_id)
    if not post:
        raise NotFoundError(resource="post", identifier=post_id)
    return post
