from fastapi import APIRouter

from app.api.routes import auth, health, nlp, posts, stats

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(nlp.router, tags=["nlp"])
api_router.include_router(posts.router, tags=["posts"])
api_router.include_router(stats.router, tags=["analytics"])
