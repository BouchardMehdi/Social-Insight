from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_nlp_analyzer, get_post_repository
from app.api.router import api_router
from app.config.settings import get_settings
from app.services.seed import DemoSeedService


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    repository = get_post_repository()
    repository.initialize()
    if settings.seed_on_startup:
        DemoSeedService(repository=repository, analyzer=get_nlp_analyzer()).seed_if_needed(
            settings.seed_posts_count
        )
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="SaaS API for social media text ingestion, NLP analysis and BigQuery analytics.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)
