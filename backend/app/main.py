"""AIDEN Platform - FastAPI Application Factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    from app.db.session import init_db
    from app.db.redis import init_redis, close_redis

    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
    
    try:
        await init_redis()
    except Exception as e:
        print(f"Warning: Redis initialization failed: {e}")
    
    yield
    
    # Shutdown
    try:
        await close_redis()
    except Exception as e:
        print(f"Warning: Redis shutdown failed: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="Agentic AI-native Development & Engineering Platform",
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API routers
    from app.api.v1.router import api_v1_router

    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": settings.app_name}

    return app


app = create_app()
