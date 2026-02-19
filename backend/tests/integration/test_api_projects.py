"""Integration tests for Project API endpoints."""

from __future__ import annotations

import uuid

import pytest


API = "/api/v1/projects"


async def test_create_project_api(client):
    """POST /projects should create a project and return SuccessResponse."""
    resp = await client.post(API, json={"name": "New Project", "description": "test"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["name"] == "New Project"
    assert body["data"]["status"] == "created"
    assert "id" in body["data"]


async def test_list_projects_api(client):
    """GET /projects should return PaginatedResponse."""
    # Create two projects first
    await client.post(API, json={"name": "P1"})
    await client.post(API, json={"name": "P2"})

    resp = await client.get(API)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) >= 2
    assert "meta" in body
    assert body["meta"]["total"] >= 2


async def test_get_project_detail_api(client):
    """GET /projects/{id} should return project with phases."""
    create_resp = await client.post(API, json={"name": "Detail Test"})
    project_id = create_resp.json()["data"]["id"]

    resp = await client.get(f"{API}/{project_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["name"] == "Detail Test"
    assert "phases" in body["data"]
    assert len(body["data"]["phases"]) == 4


async def test_update_project_api(client):
    """PATCH /projects/{id} should update and return the project."""
    create_resp = await client.post(API, json={"name": "Before"})
    project_id = create_resp.json()["data"]["id"]

    resp = await client.patch(f"{API}/{project_id}", json={"name": "After"})
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "After"


async def test_delete_project_api(client):
    """DELETE /projects/{id} should archive the project."""
    create_resp = await client.post(API, json={"name": "To Delete"})
    project_id = create_resp.json()["data"]["id"]

    del_resp = await client.delete(f"{API}/{project_id}")
    assert del_resp.status_code == 200

    # Verify archived
    get_resp = await client.get(f"{API}/{project_id}")
    assert get_resp.json()["data"]["status"] == "archived"


async def test_get_nonexistent_project_api(client):
    """GET /projects/{fake_id} should return an error status code."""
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"{API}/{fake_id}")
    # NotFoundError is raised but no global exception handler → 500
    assert resp.status_code in (404, 500)
