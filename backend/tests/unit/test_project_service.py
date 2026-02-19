"""Unit tests for ProjectService."""

from __future__ import annotations

import uuid

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService


async def test_create_project(db_session):
    """Creating a project should also create 4 default phases."""
    service = ProjectService(db_session)
    project = await service.create_project(
        ProjectCreate(name="Alpha", description="desc")
    )
    await db_session.commit()

    assert project.name == "Alpha"
    assert project.status == "created"

    fetched = await service.get_project(project.id)
    assert len(fetched.phases) == 4
    phase_types = [p.phase_type for p in fetched.phases]
    assert phase_types == ["analysis", "design", "development", "testing"]


async def test_create_project_with_config(db_session):
    """Config dict should be persisted on the project."""
    service = ProjectService(db_session)
    cfg = {"llm_model": "gpt-4.1", "temperature": 0.2}
    project = await service.create_project(
        ProjectCreate(name="Beta", config=cfg)
    )
    await db_session.commit()

    fetched = await service.get_project(project.id)
    assert fetched.config["llm_model"] == "gpt-4.1"
    assert fetched.config["temperature"] == 0.2


async def test_get_project_not_found(db_session):
    """Fetching a nonexistent project should raise NotFoundError."""
    service = ProjectService(db_session)
    fake_id = uuid.uuid4()
    with pytest.raises(NotFoundError):
        await service.get_project(fake_id)


async def test_list_projects_pagination(db_session):
    """list_projects should respect offset and limit."""
    service = ProjectService(db_session)
    for i in range(5):
        await service.create_project(ProjectCreate(name=f"Proj-{i}"))
    await db_session.commit()

    projects, total = await service.list_projects(offset=0, limit=3)
    assert total == 5
    assert len(projects) == 3

    projects2, _ = await service.list_projects(offset=3, limit=3)
    assert len(projects2) == 2


async def test_start_project(db_session):
    """Starting a project should transition status and mark analysis phase ready."""
    service = ProjectService(db_session)
    project = await service.create_project(ProjectCreate(name="Gamma"))
    await db_session.commit()

    started = await service.start_project(project.id)
    assert started.status == "analysis"
    assert started.current_phase == "analysis"

    analysis_phase = next(p for p in started.phases if p.phase_type == "analysis")
    assert analysis_phase.status == "ready"


async def test_start_project_invalid_status(db_session):
    """Starting a project that is already in progress should raise ValueError."""
    service = ProjectService(db_session)
    project = await service.create_project(ProjectCreate(name="Delta"))
    await db_session.commit()

    await service.start_project(project.id)
    await db_session.commit()

    with pytest.raises(ValueError, match="Cannot start project"):
        await service.start_project(project.id)


async def test_delete_project_soft(db_session):
    """Deleting a project should archive it, not remove it from DB."""
    service = ProjectService(db_session)
    project = await service.create_project(ProjectCreate(name="Epsilon"))
    await db_session.commit()

    await service.delete_project(project.id)
    await db_session.commit()

    # Should still be fetchable but with archived status
    fetched = await service.get_project(project.id)
    assert fetched.status == "archived"
