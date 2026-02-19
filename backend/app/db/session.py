"""Async SQLAlchemy database session management."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


def _build_engine():
    """Build the async engine based on configuration."""
    url = settings.effective_database_url
    is_sqlite = url.startswith("sqlite")

    kwargs = {
        "echo": settings.debug,
    }

    if is_sqlite:
        # SQLite doesn't support pool_size / max_overflow
        from sqlalchemy.pool import StaticPool
        kwargs["poolclass"] = StaticPool
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_size"] = settings.db_pool_size
        kwargs["max_overflow"] = settings.db_max_overflow

    return create_async_engine(url, **kwargs)


engine = _build_engine()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database — create tables for SQLite dev mode."""
    if settings.use_sqlite:
        from app.models.base import Base
        # Import all models so they register with Base.metadata
        import app.models.user  # noqa: F401
        import app.models.project  # noqa: F401
        import app.models.task  # noqa: F401
        import app.models.document  # noqa: F401
        import app.models.deliverable  # noqa: F401
        import app.models.agent  # noqa: F401
        import app.models.hitl  # noqa: F401

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[DEV] SQLite tables created successfully")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
