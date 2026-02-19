"""Shared pytest fixtures for AIDEN backend tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Import all models so Base.metadata knows about them
from app.models.base import Base
import app.models.user  # noqa: F401
import app.models.project  # noqa: F401
import app.models.task  # noqa: F401
import app.models.document  # noqa: F401
import app.models.deliverable  # noqa: F401
import app.models.agent  # noqa: F401
import app.models.hitl  # noqa: F401

from app.db.session import get_db
from app.schemas.project import ProjectCreate
from app.services.project_service import ProjectService


@pytest.fixture
async def db_engine():
    """Create an in-memory SQLite engine for test isolation."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Provide an async session bound to the test engine."""
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    """Async HTTP client wired to the FastAPI app with overridden deps."""
    from app.main import app

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    # Inject mock singletons so endpoints that need them don't crash
    app.state.llm_provider = MagicMock()
    app.state.rag_pipeline = MagicMock()
    app.state.event_bus = MagicMock()

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_project(db_session) -> "app.models.project.Project":
    """Create and return a sample project with default phases."""
    service = ProjectService(db_session)
    project = await service.create_project(
        ProjectCreate(name="Test Project", description="A test project")
    )
    await db_session.commit()
    return project
